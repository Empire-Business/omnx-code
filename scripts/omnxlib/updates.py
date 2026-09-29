"""Opt-in release availability checks and inert side-by-side staging.

The running package is never changed here. GitHub checksums verify artifact
bytes over the configured HTTPS source; they are not signatures.
"""
from __future__ import annotations
import datetime as dt
from functools import cmp_to_key
import json
import urllib.error
import urllib.request
from urllib.parse import urlsplit
from .core import *
from .distribution import compare_versions

POLICY='.omnx/local/update-policy.json'
STATE='.omnx/local/update-check.json'
API='https://api.github.com/repos/Empire-Business/omnx-code/releases?per_page=20'
REPO='https://github.com/Empire-Business/omnx-code/releases/download/'
MAX_ARCHIVE=64*1024*1024

class GuardedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        parsed=urlsplit(newurl)
        require(parsed.scheme=='https' and parsed.hostname in {'api.github.com','github.com','release-assets.githubusercontent.com','objects.githubusercontent.com'},'update_redirect','Redirecionamento para origem fora da lista oficial recusado.',5)
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def _read_policy(fs):
    data=fs.data(POLICY)
    if data is None:return None,None
    validate(data,schema('update-policy'));return data,fs.hash(POLICY)

def _read_state(fs):
    data=fs.data(STATE)
    if data is None:return None,None
    validate(data,schema('update-state'));return data,fs.hash(STATE)

def configure(fs,enabled,channel=None,interval=None,consent=False,expected=None):
    from .project import ensure_writable
    ensure_writable(fs);require(channel is None or channel in ('stable','rc'),'invalid_channel','Canal de atualização inválido.')
    require(interval is None or (type(interval)is int and 1<=interval<=168),'invalid_interval','Intervalo permitido: 1 a 168 horas.')
    require(type(enabled)is bool,'invalid_policy','Estado da política inválido.')
    with metadata_lock(fs,'update-policy'):
        ensure_writable(fs);old,old_hash=_read_policy(fs)
        if expected is not None:require(old_hash==expected,'stale_state','Política mudou; releia antes de atualizar.',3)
        if enabled:require(consent or bool(old and old['enabled']),'consent_required','Ativar consulta e staging automáticos exige consentimento explícito uma vez.',5)
        selected_channel=channel or (old or {}).get('channel','stable')
        selected_interval=interval if interval is not None else (old or {}).get('check_interval_hours',24)
        if enabled:
            consented_at=old['consented_at'] if old and old['enabled'] else now()
            data={'schema_version':1,'enabled':True,'channel':selected_channel,'check_interval_hours':selected_interval,'consented_at':consented_at,'consent_scope':'availability-check-and-stage-official-release'}
        else:
            data={'schema_version':1,'enabled':False,'channel':selected_channel,'check_interval_hours':selected_interval,'consented_at':old['consented_at'] if old else now(),'consent_scope':'availability-check-and-stage-official-release'}
        validate(data,schema('update-policy'));raw=json_bytes(data)
        if fs.read(POLICY)==raw:return result('Política já está neste estado.',policy=data,sha256=old_hash)
        fs.write(POLICY,raw,old_hash)
    return result('Política local atualizada; nenhuma versão em uso foi alterada.',changed_paths=[POLICY],policy=data,sha256=digest(raw),limitations=['Escopo desta autorização: verificar e preparar releases oficiais compatíveis. Ativação no host continua separada.'])

def read_console_state(fs):
    try:state,_=_read_state(fs);return state
    except (MethodError,OSError):return None

def _http_json(url,limit,timeout=4):
    parsed=urlsplit(url)
    require(parsed.scheme=='https' and parsed.hostname in {'api.github.com','github.com'},'update_origin','Origem de atualização não permitida.',5)
    request=urllib.request.Request(url,headers={'Accept':'application/vnd.github+json','User-Agent':'OMNX-Code updater','X-GitHub-Api-Version':'2026-03-10'})
    opener=urllib.request.build_opener(GuardedRedirect())
    with opener.open(request,timeout=timeout) as response:
        require(response.status==200,'update_http','Origem de atualização retornou resposta inválida.',4)
        raw=response.read(limit+1);require(len(raw)<=limit,'update_response_limit','Resposta de atualização excede o limite.',4)
        return raw

def _version(tag):
    require(isinstance(tag,str) and len(tag)<=90,'invalid_release','Tag de release inválida.')
    return tag[1:] if tag.startswith('v') else tag

def _select_release(releases,channel,installed):
    require(type(releases)is list,'invalid_release_index','Índice de releases inválido.')
    candidates=[]
    for row in releases[:20]:
        if type(row)is not dict or row.get('draft') is True:continue
        try:version=_version(row.get('tag_name',''))
        except MethodError:continue
        if channel=='stable' and (row.get('prerelease') is True or '-' in version):continue
        if channel=='rc' and (row.get('prerelease') is not True or '-' not in version):continue
        try:
            if compare_versions(version,installed)>0:candidates.append((version,row))
        except MethodError:continue
    if not candidates:return None
    return sorted(candidates,key=cmp_to_key(lambda a,b:compare_versions(a[0],b[0])))[-1][1]

def should_check(fs):
    try:
        policy,_=_read_policy(fs);state,_=_read_state(fs)
        if not policy or not policy['enabled']:return False
        if not state:return True
        age=(dt.datetime.now(dt.timezone.utc)-timestamp(state['checked_at']).astimezone(dt.timezone.utc)).total_seconds()
        return age>=policy['check_interval_hours']*3600
    except Exception:return False

def _compatibility(files,manifest,version,project_schema):
    require(manifest.get('name')=='omnx-code' and manifest.get('version')==version,'release_manifest','Tag e manifesto não correspondem.',5)
    require(manifest.get('audit_contract_versions')==['2.0'],'release_contract','Contrato de auditoria incompatível.',5)
    require(project_schema in manifest.get('console',{}).get('project_schema_versions',[]),'release_project_schema','Projeto fora da faixa do Console candidato.',5)
    console=load_data(files.get('console/console-manifest.json',b''))
    require(console.get('version')==manifest.get('console',{}).get('version') and project_schema in console.get('project_schema_versions',[]),'release_console','Console e pacote não são coerentes.',5)

def _save_state(fs,policy,installed,status,summary,*,version=None,sha=None,stage=None,expected=None):
    state={'schema_version':1,'channel':policy['channel'],'installed_version':installed,'candidate_version':version,'status':status,'checked_at':now(),'artifact_sha256':sha,'stage_path':stage,'summary':summary[:500],'activation':'manual_host_selection_required' if status=='staged' else 'not_activated'}
    validate(state,schema('update-state'));raw=json_bytes(state);fs.write(STATE,raw,expected)
    return state

def auto_check(fs,*,force=False):
    from .project import ensure_writable
    from . import distribution
    ensure_writable(fs);manifest=load_data((PACKAGE/'manifest.json').read_bytes());installed=manifest['version']
    try:
        with metadata_lock(fs,'updates'):
            ensure_writable(fs);policy,_=_read_policy(fs);state,state_hash=_read_state(fs)
            if not policy or not policy['enabled']:
                return result('Consulta automática desativada; rede não foi consultada.',status='disabled',candidate=None)
            if not force and state:
                age=(dt.datetime.now(dt.timezone.utc)-timestamp(state['checked_at']).astimezone(dt.timezone.utc)).total_seconds()
                if age<policy['check_interval_hours']*3600:return result('Cache dentro do intervalo configurado; rede não foi consultada.',update_state=state,cached=True)
            releases=load_data(_http_json(API,2*1024*1024));release=_select_release(releases,policy['channel'],installed)
            if release is None:
                saved=_save_state(fs,policy,installed,'no_update','Nenhuma versão posterior compatível neste canal.',expected=state_hash)
                return result(saved['summary'],update_state=saved,cached=False)
            version=_version(release.get('tag_name',''));expected_prefix='omnx-code-'+version
            assets=release.get('assets',[])
            asset=next((x for x in assets if isinstance(x,dict) and x.get('name') in (expected_prefix+'.zip','omnx-code.zip') and isinstance(x.get('browser_download_url'),str)),None)
            if not asset or not isinstance(asset.get('digest'),str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',asset['digest']):
                saved=_save_state(fs,policy,installed,'release_without_artifact','Release encontrada, mas não há ZIP com SHA-256 publicado pelo GitHub.',version=version,expected=state_hash)
                return result(saved['summary'],update_state=saved,cached=False)
            url=asset['browser_download_url'];parsed=urlsplit(url)
            require(parsed.scheme=='https' and parsed.hostname=='github.com' and parsed.path.startswith('/Empire-Business/omnx-code/releases/download/'),'update_asset_origin','Asset não pertence à release oficial.',5)
            archive=_http_json(url,MAX_ARCHIVE,timeout=5);sha=asset['digest'].split(':',1)[1]
            require(digest(archive)==sha,'artifact_integrity','ZIP difere do SHA-256 publicado.',5)
            download=f'.omnx/local/update-downloads/omnx-code-{version}-{sha[:12]}.zip';expected_download=fs.hash(download)
            if expected_download is not None:require(expected_download==sha,'download_collision','Arquivo local de staging já existe com bytes diferentes.',5)
            else:fs.write(download,archive,None)
            files,candidate=distribution.inspect_archive(str(fs.path(download)),sha)
            try:_compatibility(files,candidate,version,fs.data('.omnx/project.yaml',yaml_ok=True)['schema_version'])
            except MethodError as exc:
                try:fs.delete(download,digest(archive))
                except (MethodError,OSError):pass
                saved=_save_state(fs,policy,installed,'incompatible',exc.summary,version=version,sha=sha,expected=state_hash)
                return result(saved['summary'],update_state=saved,cached=False)
            with fs.parent('.omnx/local/method-updates/.staging',create=True):pass
            destination=fs.root/'.omnx/local/method-updates'/f'omnx-code-{version}'
            plan=distribution.plan(str(fs.path(download)),sha,str(destination),installed)
            distribution.apply(plan,plan['plan_digest'])
            try:fs.delete(download,digest(archive))
            except (MethodError,OSError):pass
            saved=_save_state(fs,policy,installed,'staged','Candidato íntegro preparado em pasta separada; runtime atual permanece fixo nesta sessão.',version=version,sha=sha,stage=str(destination.relative_to(fs.root)),expected=state_hash)
            return result(saved['summary'],update_state=saved,cached=False,limitations=['Checksum do GitHub verifica bytes, não assinatura. O host precisa selecionar o caminho versionado numa sessão futura; nenhum arquivo ativo foi substituído.'])
    except Exception as exc:
        if isinstance(exc,MethodError) and exc.code=='locked':
            return result('Outra sessão já está verificando/preparando uma release; o runtime atual foi preservado.',status='in_progress',update_state=read_console_state(fs),cached=True)
        try:
            policy,_=_read_policy(fs);old,old_hash=_read_state(fs)
            if policy and policy['enabled']:
                with metadata_lock(fs,'updates'):
                    current,current_hash=_read_state(fs)
                    saved=_save_state(fs,policy,installed,'unavailable','Consulta ou staging indisponível; a versão instalada foi preservada.',expected=current_hash)
                    return {'status':'warning','code':'UPDATE_UNAVAILABLE','summary':saved['summary'],'changed_paths':[STATE],'limitations':[type(exc).__name__],'update_state':saved}
        except Exception:pass
        return {'status':'warning','code':'UPDATE_UNAVAILABLE','summary':'Consulta ou staging indisponível; a versão instalada foi preservada.','changed_paths':[],'limitations':[type(exc).__name__]}
