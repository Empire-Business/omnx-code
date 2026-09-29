"""Configurable, host-neutral model and effort recommendations.

The policy never calls a model and never claims that a host applied the result.
"""
from __future__ import annotations
import re
from .core import *

PROFILES=('deterministic','economical','balanced','advanced')
EFFORTS=('low','medium','high','xhigh')
PATH='.omnx/local/model-policy.json'

def defaults():
    return {'schema_version':1,'profiles':{name:{'model':None,'effort':None} for name in PROFILES}}

def read(fs):
    data=fs.data(PATH)
    if data is None:return defaults(),None
    validate(data,schema('model-policy'))
    return data,fs.hash(PATH)

def configure(fs,profile,model=None,effort=None,expected=None):
    from .project import ensure_writable
    ensure_writable(fs)
    require(profile in PROFILES,'invalid_profile','Perfil de modelo inválido.')
    require(model is None or (isinstance(model,str) and 1<=len(model)<=160 and not any(ord(c)<32 for c in model)),'invalid_model','Nome de modelo inválido.')
    require(effort is None or effort in EFFORTS,'invalid_effort','Esforço não suportado pelo esquema OMNX.')
    with metadata_lock(fs,'model-policy'):
        ensure_writable(fs);old,old_hash=read(fs)
        if expected is not None:require(old_hash==expected,'stale_state','Política mudou; releia antes de gravar.',3)
        profiles={**old['profiles'],profile:{'model':model,'effort':effort}}
        data={'schema_version':1,'profiles':profiles};validate(data,schema('model-policy'))
        raw=json_bytes(data)
        if raw==fs.read(PATH):return result('Perfil sem alterações.',policy=data,sha256=old_hash)
        fs.write(PATH,raw,old_hash)
    return result('Mapeamento local do perfil atualizado; o host não foi reconfigurado.',changed_paths=[PATH],policy=data,sha256=digest(raw),limitations=['A configuração é local à cópia do projeto. O modelo efetivo continua não confirmado até observação do host.'])

def choose(*,risk='medium',ambiguity='medium',verification='objective',reasoning_needed=True,configured=None):
    require(risk in ('low','medium','high','critical'),'invalid_risk','Risco inválido.')
    require(ambiguity in ('low','medium','high'),'invalid_ambiguity','Ambiguidade inválida.')
    require(verification in ('script','objective','judgment'),'invalid_verification','Tipo de verificação inválido.')
    require(type(reasoning_needed)is bool,'invalid_reasoning','reasoning_needed deve ser booleano.')
    if not reasoning_needed and verification=='script':
        profile='deterministic';reason='Validação mecânica e verificável por script; não exige raciocínio.'
    elif risk in ('high','critical') or ambiguity=='high':
        profile='advanced';reason='Risco ou ambiguidade exige análise mais forte; decisão não depende do tamanho do diff.'
    elif risk=='low' and ambiguity=='low' and verification in ('script','objective'):
        profile='economical';reason='Escopo claro, baixo risco e verificação objetiva favorecem menor custo esperado.'
    else:
        profile='balanced';reason='Implementação comum ou evidência insuficiente para outro perfil.'
    entry=(configured or defaults())['profiles'][profile]
    return {'profile':profile,'requested_model':entry['model'],'effective_model':None,'requested_effort':entry['effort'],'effective_effort':None,'effective_status':'not_observed','reason':reason,'escalated_from':None,'cost_status':'unknown','cost_value':None}

def infer(prompt,configured=None):
    """Conservative local hint from an implementation request; never an LLM call."""
    lower=prompt.lower()
    sensitive=re.search(r'\b(auth|authentication|authorization|permission|isolation|tenant|payment|billing|credential|secret|migra(?:tion|te)|database|security|seguran[cç]a|autentica[cç][aã]o|autoriza[cç][aã]o|pagamento|credencial|migra[cç][aã]o|banco de dados)\b',lower)
    high_ambiguity=bool(re.search(r'\b(architecture|redesign|systemic|arquitetura|redesenh|sist[eê]mic)\b',lower))
    clear=bool(re.match(r'^\s*(please\s+)?(implement|fix|update|add|build|change|create|corrija|implemente|atualize|adicione|crie|construa|edite)\b',lower))
    return choose(risk='high' if sensitive else 'low' if clear else 'medium',ambiguity='high' if high_ambiguity else 'low' if clear else 'medium',verification='objective' if clear else 'judgment',reasoning_needed=True,configured=configured)

def recommend(fs,task_id,risk=None,ambiguity='medium',verification='objective',reasoning_needed=True):
    from .tasks import Store
    _,task,_,sha=Store(fs).read_record(task_id);config,_=read(fs)
    security=(task.get('impact') or {}).get('security','S1')
    title=task.get('title','').lower()
    sensitive=bool(re.search(r'\b(auth|permission|isolation|tenant|payment|credential|secret|migration|database|security|seguran[cç]a|autentica[cç][aã]o|autoriza[cç][aã]o|pagamento|credencial|migra[cç][aã]o)\b',title))
    effective_risk=risk or ('critical' if security=='S3' else 'high' if security=='S2' or sensitive else 'medium')
    recommendation=choose(risk=effective_risk,ambiguity=ambiguity,verification=verification,reasoning_needed=reasoning_needed,configured=config)
    return result('Recomendação sem chamada de modelo; modelo efetivo e custo não observados.',task_id=task_id,task_sha256=sha,recommendation=recommendation)
