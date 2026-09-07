"""Offline DOM test transport. NOT browser HTTP/CSP/cookie end-to-end coverage.

Only synthetic files created by the test are reachable. It calls the engine
in-process; it does not tunnel around browser/enterprise network restrictions.
The production app.js stays unchanged. Browser history, UUID, clipboard and
fetch are explicit fixture doubles because about:blank is not a secure origin.
"""
import base64, json, re, urllib.parse
from copy import deepcopy
from omnxlib.core import *
from omnxlib import console as cs, projection, previews, tasks, decisions

class OfflineTransport:
    def __init__(self, allowed_roots):
        self.allowed_roots={str(Path(r).resolve()) for r in allowed_roots}
        self.calls=[]
    def request(self,path,options=None):
        try:
            return {'status':200,'body':self.dispatch(path,options or {})}
        except MethodError as e:
            return {'status':409 if e.exit_code==3 else 403 if e.exit_code==5 else 400,
                    'body':{'error':e.code,'summary':e.summary}}
    def dispatch(self,path,options):
        self.calls.append(path.split('?')[0]);u=urllib.parse.urlsplit(path)
        require(not u.netloc,'fixture_scope','Fixture accepts relative API paths only.')
        q=dict(urllib.parse.parse_qsl(u.query));data=json.loads(options.get('body') or '{}')
        if u.path=='/api/session':return {'csrf':'offline-fixture-not-a-real-session'}
        if u.path=='/api/projects':
            rows=[cs._read_project(x['path']) for x in cs._catalog_read()['projects']]
            return {'projects':rows,'overview':cs.overview(rows),'refreshed_at':now()}
        wid=q.get('workspace_id') or data.get('workspace_id');item=cs.find_workspace(wid)
        require(str(Path(item['path']).resolve()) in self.allowed_roots,'fixture_scope','Unknown synthetic root.')
        fs=RootFS(item['path']);p=cs._read_project(fs.root)
        if u.path=='/api/project':
            collection=q.get('collection')
            if collection:
                rows=p[collection]
                if q.get('status'):rows=[r for r in rows if r.get('status')==q['status']]
                start=int(q.get('offset',0));limit=int(q.get('limit',100))
                return {'items':rows[start:start+limit],'total':len(rows),'offset':start,'partial':p['partial'],'errors':p['errors'],'revision':p['revision']}
            p['totals']={k:len(p[k]) for k in ('tasks','decisions','mockups')}
            for k in ('tasks','decisions','mockups'):p[k]=p[k][:200]
            return p
        if u.path=='/api/task':return projection.task_detail(fs,q['id'])
        if u.path=='/api/decision':return projection.decision_detail(fs,q['id'])
        if u.path=='/api/prompt':return {'prompt':cs.prompt_for_task(p,q['task_id'],q.get('mode','compact'))}
        if u.path=='/api/diagnostics':return {'errors':p['errors'],'counts':p['counts'],'scope':'offline-fixture'}
        if u.path=='/api/preview':
            if data.get('decision_id'):
                _,d,sha=decisions.Store(fs).read_record(data['decision_id'])
                require(sha==data['expected_sha256'],'stale_state','A decisão mudou. Reabra.',3)
                rel=d['subject_ref'];current=previews.bundle_manifest(fs,rel)
                require(current==d['subject_manifest'],'stale_subject','Os arquivos mudaram. Reabra.',3)
            else:
                m=next(m for m in p['mockups'] if m['id']==data['preview_id']);rel=m['path'];current=previews.bundle_manifest(fs,rel)
            raw=fs.read(rel);ext=Path(rel).suffix.lower()
            if ext in ('.html','.htm'):
                content=previews.render_html(raw,rel,[x['path'] for x in current],'fixture').decode('utf-8')
                # Assets in these fixtures are inline. No networking or real grant.
                return {'url':'data:text/html;base64,'+base64.b64encode(content.encode()).decode(),'kind':'html'}
            return {'url':'data:image/png;base64,'+base64.b64encode(raw).decode(),'kind':'image'}
        if u.path=='/api/decision/update':
            return decisions.Store(fs).update(data['decision_id'],data['expected_sha256'],status=data['status'],selected_option=data.get('selected_option'),feedback=data.get('feedback'),authority_ref='test:offline-dom-local-user')
        if u.path=='/api/task/transition':
            patch={}
            if data.get('blocked_reason'):patch['blocked_reason']=data['blocked_reason']
            if data['to']=='in_progress':patch['owner']='test:offline-dom-user'
            return tasks.Store(fs).update(data['task_id'],patch,data['expected_sha256'],transition=data['to'])
        raise MethodError('fixture_route','Endpoint not implemented by the offline test transport.')

FIXTURE_JS=r'''// Test doubles; never included in production assets.
history.replaceState=()=>{};
crypto.randomUUID=()=>"10000000-1000-4000-8000-"+String(++globalThis.__fixtureCounter).padStart(12,'0');
globalThis.__fixtureCounter=0;
globalThis.__fixtureClipboard='';
Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async t=>{globalThis.__fixtureClipboard=t},readText:async()=>globalThis.__fixtureClipboard}});
// Offline preview documents use srcdoc, never a network request or URL grant.
const originalCreate=document.createElement.bind(document);
document.createElement=function(tag,...args){const e=originalCreate(tag,...args);if(String(tag).toLowerCase()==='iframe')Object.defineProperty(e,'src',{set(url){if(!url.startsWith('data:text/html;base64,'))throw new Error('Fixture iframe must remain offline');this.srcdoc=new TextDecoder().decode(Uint8Array.from(atob(url.split(',')[1]),c=>c.charCodeAt(0)));},get(){return 'about:srcdoc';}});return e;};
globalThis.fetch=async(path,opts={})=>{const r=await globalThis.__offlineRequest(String(path),{method:opts.method,body:opts.body});return {ok:r.status>=200&&r.status<300,status:r.status,json:async()=>r.body}};
'''

def mount(page,package,transport):
    page.expose_function('__offlineRequest',transport.request)
    html=(package/'console/assets/index.html').read_text()
    html=re.sub(r'<link\b[^>]*>','',html,flags=re.I)
    html=re.sub(r'<script\b[^>]*>.*?</script>','',html,flags=re.I|re.S)
    page.set_content(html)
    page.add_style_tag(path=str(package/'console/assets/style.css'))
    page.add_script_tag(content=FIXTURE_JS)
    page.add_script_tag(path=str(package/'console/assets/app.js'))
