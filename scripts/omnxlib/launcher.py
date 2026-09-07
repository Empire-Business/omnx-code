"""Explicit local installation and one-click launcher; Python is a prerequisite.

No administrator access, remote download or silently overwritten installation.
The package remains independently removable from project data.
"""
from __future__ import annotations
import platform
import plistlib
import shlex
import shutil
import subprocess
import time
import urllib.request
import urllib.error
import webbrowser
from .core import *

ENTRY=PACKAGE/'scripts'/'omnx.py'

def _http(port,path,token=None):
    require(type(port)is int and 1024<=port<=65535,'invalid_instance','Porta da instância inválida.')
    url=f'http://127.0.0.1:{port}{path}'
    req=urllib.request.Request(url,headers={'Content-Type':'application/json',**({'X-OMNX-Launcher':token} if token else {})},data=b'{}' if token else None)
    # Do not inherit proxy configuration for the local control connection.
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req,timeout=2) as r:
        raw=r.read(65537);require(len(raw)<=65536,'invalid_instance','Resposta local excedeu limite.')
        return load_data(raw)

def _descriptor_name():
    version=load_data((PACKAGE/'manifest.json').read_bytes())['version']
    return 'instance-'+digest((str(PACKAGE)+':'+version).encode())[:24]+'.json'

def _existing(fs,name):
    raw=fs.read(name,65536)
    if raw is None:return None
    d=load_data(raw)
    require(type(d)is dict and d.get('schema_version')==1 and isinstance(d.get('launcher_token'),str) and len(d['launcher_token'])>=32 and type(d.get('pid'))is int and d['pid']>0 and type(d.get('port'))is int and 1024<=d['port']<=65535 and isinstance(d.get('instance_id'),str),'invalid_instance','Registro de instância inválido; preserve e diagnostique.',3)
    try:
        h=_http(d['port'],'/api/health')
        require(h.get('instance_id')==d.get('instance_id'),'instance_changed','A porta pertence a outra instância; não enviaremos credenciais.',3)
        return d
    except (urllib.error.URLError,TimeoutError,ConnectionError):
        # Do not kill arbitrary PIDs. Delete only the stale descriptor. A live
        # but unresponsive expected PID requires explicit diagnosis.
        alive=False
        if os.name=='posix':
            try:os.kill(d.get('pid',-1),0);alive=True
            except PermissionError:alive=True
            except (ProcessLookupError,OSError):pass
        require(not alive,'instance_unresponsive','Console anterior não responde. Use diagnóstico/encerramento manual, sem iniciar outra cópia.',3)
        fs.delete(name,digest(raw));return None

def open_console(root=None,port=0,open_browser=True):
    from . import console as cs
    if root is not None:cs.register(root)
    cs.CATALOG_DIR.mkdir(mode=0o700,parents=True,exist_ok=True);fs=RootFS(cs.CATALOG_DIR);name=_descriptor_name()
    with metadata_lock(fs,'startup'):
        d=_existing(fs,name)
        reused=d is not None
        if d is None:
            logname=name.replace('.json','.log')
            log=fs.path(logname)
            flags=os.O_WRONLY|os.O_CREAT|os.O_APPEND|getattr(os,'O_NOFOLLOW',0)
            fd=os.open(log,flags,0o600)
            require(os.fstat(fd).st_nlink==1,'unsafe_link','Log de abertura não pode ser hardlink.',5)
            args=[sys.executable,str(ENTRY),'console','serve','--port',str(port),'--no-browser','--ready-file',str(fs.path(name))]
            kwargs={'cwd':str(PACKAGE),'stdin':subprocess.DEVNULL,'stdout':fd,'stderr':fd,'close_fds':True,'env':{**os.environ,'OMNX_CONSOLE_HOME':str(cs.CATALOG_DIR),'PYTHONDONTWRITEBYTECODE':'1'}}
            if os.name=='nt':kwargs['creationflags']=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.DETACHED_PROCESS
            else:kwargs['start_new_session']=True
            try:child=subprocess.Popen(args,**kwargs)
            finally:os.close(fd)
            deadline=time.monotonic()+10
            while time.monotonic()<deadline:
                if child.poll() is not None:raise MethodError('console_start_failed','Console encerrou durante a abertura; consulte o log local.',4)
                raw=fs.read(name,65536)
                if raw:
                    d=load_data(raw);break
                time.sleep(.05)
            require(d is not None,'console_start_timeout','Abertura ainda não confirmada. Não iniciamos outra cópia.',4)
        launch=_http(d['port'],'/api/launch',d['launcher_token'])
        require(launch.get('instance_id')==d['instance_id'],'instance_changed','Instância mudou; abertura cancelada.',3)
    if open_browser:webbrowser.open(launch['url'])
    return result('Console aberto.' if not reused else 'Console já estava aberto; instância reutilizada.',console_url=launch['url'],reused=reused,pid=d['pid'],limitations=['Python local é necessário. O ícone não é um binário nativo assinado. Nenhuma IA foi chamada.'])

def stop_console():
    from . import console as cs
    if not cs.CATALOG_DIR.exists():return result('Nenhuma instância registrada.')
    fs=RootFS(cs.CATALOG_DIR);d=_existing(fs,_descriptor_name())
    if not d:return result('Nenhuma instância ativa desta versão.')
    _http(d['port'],'/api/shutdown',d['launcher_token'])
    return result('Encerramento solicitado à instância verificada; projetos preservados.')

def install(destination):
    # Explicitly copy the trusted, running package into a stable new directory.
    from .cli import verify_package
    verify_package()
    dest=Path(destination).expanduser().absolute();parent=RootFS(dest.parent);parent.path(dest.name)
    require(not dest.exists(),'occupied_installation','Escolha uma pasta nova/versionada; não sobrescreveremos uma instalação.',3)
    stage=dest.parent/('.omnx-local-install-'+uuid.uuid4().hex);stage.mkdir(mode=0o700)
    try:
        inventory=load_data((PACKAGE/'integrity.json').read_bytes())['files']
        stagefs=RootFS(stage)
        for rel in [*inventory,'integrity.json']:
            raw=RootFS(PACKAGE).read(rel);stagefs.write(rel,raw,None,0o644)
        require(not dest.exists(),'installation_race','Destino apareceu durante a cópia.',3)
        os.rename(stage,dest)
    except Exception:
        # Inert staging is preserved for diagnostics, not promoted as installed.
        raise
    return result('Cópia local instalada em pasta estável. Crie o atalho usando o comando desta nova pasta.',changed_paths=[str(dest)],entrypoint=str(dest/'scripts'/'omnx.py'))

def _desktop_quote(s):
    # Desktop Entry Exec is NOT a shell command. Escape field codes separately.
    return '"'+str(s).replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$').replace('%','%%')+'"'

def create(destination=None,name='OMNX Console'):
    system=platform.system().lower();dest=Path(destination).expanduser().absolute() if destination else Path.home()/'Desktop'
    require(dest.is_dir(),'launcher_destination','Pasta de atalhos não encontrada. Informe --destination.',4)
    require(isinstance(name,str) and re.fullmatch(r'[A-Za-z0-9 _-]{1,70}',name),'invalid_launcher_name','Nome de atalho inválido.')
    fs=RootFS(dest);python=str(Path(sys.executable).absolute());entry=str(ENTRY)
    if system=='darwin':
        app=name+'.app';require(not fs.path(app).exists(),'launcher_exists','Atalho já existe; não sobrescreveremos.',3)
        script=f'#!/bin/sh\nexec {shlex.quote(python)} {shlex.quote(entry)} console open\n'.encode()
        fs.write(app+'/Contents/MacOS/omnx-console',script,None,0o700)
        info={'CFBundleName':name,'CFBundleDisplayName':name,'CFBundleExecutable':'omnx-console','CFBundleIdentifier':'com.omnx.console','CFBundlePackageType':'APPL'}
        fs.write(app+'/Contents/Info.plist',plistlib.dumps(info),None,0o644)
        target=dest/app;limitation='Bundle de launcher não assinado/notarizado; requer Python no caminho instalado e homologação macOS.'
    elif system=='windows':
        rel=name+'.cmd';script='@echo off\r\nsetlocal DisableDelayedExpansion\r\n"'+python.replace('%','%%')+'" "'+entry.replace('%','%%')+'" console open\r\nif errorlevel 1 pause\r\n'
        fs.write(rel,script.encode('utf-8'),None,0o600);target=dest/rel
        limitation='Atalho .cmd usa o Python desta instalação. Requer homologação Windows; não é .exe nativo.'
    else:
        rel=name.replace(' ','-').lower()+'.desktop'
        script='[Desktop Entry]\nType=Application\nName='+name+'\nExec='+_desktop_quote(python)+' '+_desktop_quote(entry)+' console open\nIcon='+str(CONSOLE_ICON())+'\nTerminal=false\nCategories=Development;\n'
        fs.write(rel,script.encode(),None,0o700);target=dest/rel
        limitation='O desktop pode exigir marcar o launcher como confiável. Use uma instalação estável, não uma pasta temporária de ZIP.'
    return result('Atalho criado sem sobrescrever arquivos existentes.',changed_paths=[str(target)],python=python,entrypoint=entry,limitations=[limitation,'Mover/remover a pasta da instalação quebra este atalho; reinstale em destino estável.'])

def CONSOLE_ICON():return PACKAGE/'console'/'assets'/'icon.svg'
