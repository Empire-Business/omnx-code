"""Decision state machine. An atomic document preserves prior revisions.

Hashes detect accidental/casual mutation, not human identity. Local CLI writes
are self-reported decisions. This is NEVER release or security attestation.
Legacy v1 decisions are visible, but must be revised/reconfirmed explicitly.
"""
from __future__ import annotations
from copy import deepcopy
from .core import *
from .previews import bundle_manifest

TERMINAL={'approved','rejected','superseded','cancelled'}
PROPOSAL_FIELDS={'type','title','question','subject_ref','subject_sha256','task_refs','options','recommended_option'}

def state(d): return {k:v for k,v in d.items() if k!='history'}

def check(d):
    validate(d,schema('decision'))
    for k in ('created_at','updated_at'):
        timestamp(d[k])
    require(timestamp(d['updated_at'])>=timestamp(d['created_at']),'invalid_time','Decisão atualizada antes de ser criada.')
    if d['schema_version']==1: return d # deliberately untrusted, read-only legacy
    opts=[o['id'] for o in d['options']]
    require(len(opts)==len(set(opts)), 'duplicate_option','IDs das opções devem ser únicos.')
    require(d['recommended_option'] is None or d['recommended_option'] in opts,'invalid_option','Recomendação não pertence às opções.')
    require(d['selected_option'] is None or d['selected_option'] in opts,'invalid_option','Escolha não pertence às opções.')
    if d['status']=='approved':
        require(not opts or d['selected_option'] in opts,'missing_option','Escolha uma opção antes de aprovar.',5)
    if d['status'] in TERMINAL:
        require(bool(d['authority_ref']) and d['decided_at'] is not None,'missing_authority','Decisão terminal exige origem e data.',5)
        timestamp(d['decided_at'])
    else:
        require(d['selected_option'] is None and d['decided_at'] is None,'invalid_decision_state','Proposta não pode carregar uma escolha aprovada.')
    if d['subject_ref']:
        from .privacy import safe_subject_path
        safe_subject_path(d['subject_ref'])
        require(d['subject_sha256'] is not None and d['subject_manifest'],'missing_subject_digest','Proposta de arquivo exige revisão de conteúdo.',5)
        bypath={x['path']:x['sha256'] for x in d['subject_manifest']}
        require(len(bypath)==len(d['subject_manifest']) and bypath.get(d['subject_ref'])==d['subject_sha256'],'invalid_subject_manifest','Manifesto de proposta inconsistente.')
    else:require(d['subject_sha256'] is None and not d['subject_manifest'],'invalid_subject_manifest','Manifesto sem arquivo principal.')
    if 'history' in d:
        # All states were stored in the same atomic write as the new state.
        expected=1
        for event in d['history']:
            previous=event['previous']
            require(previous['id']==d['id'] and previous['revision']==expected and event['sha256']==object_digest(previous),'decision_history_invalid','Histórico de revisões inconsistente.',3)
            timestamp(event['recorded_at']);expected+=1
        require(d['revision']==expected,'decision_history_invalid','Histórico não corresponde à revisão atual.',3)
    return d

class Store:
    def __init__(self,fs):self.fs=fs
    def read_record(self,did):
        require(isinstance(did,str) and re.fullmatch(r'DEC-[A-Za-z0-9][A-Za-z0-9-]{1,90}',did),'invalid_id','ID de decisão inválido.')
        rel=f'.omnx/decisions/{did}.json';raw=self.fs.read(rel)
        require(raw is not None,'missing_decision','Decisão não encontrada.',4)
        d=check(load_data(raw));require(d['id']==did,'decision_filename','ID e nome de arquivo divergem.',3)
        return rel,d,digest(raw)
    def entries(self):
        base=self.fs.path('.omnx/decisions')
        if not base.exists():return []
        return [(rel,d) for rel,d,_ in (self.read_record(p.stem) for p in sorted(base.glob('DEC-*.json')))]
    def get(self,did):
        rel,d,_=self.read_record(did);return rel,d
    def _bind(self,d):
        if d.get('subject_ref'):
            manifest=bundle_manifest(self.fs,d['subject_ref']);actual=next(x['sha256'] for x in manifest if x['path']==d['subject_ref'])
            supplied=d.get('subject_sha256');require(supplied is None or supplied==actual,'stale_subject','Hash fornecido não corresponde à proposta atual.',3)
            d['subject_sha256']=actual;d['subject_manifest']=manifest
        else:
            require(d.get('subject_sha256') is None,'invalid_subject_manifest','Hash sem arquivo principal.')
            d['subject_sha256']=None;d['subject_manifest']=[]
        return d
    def _task_refs(self,d):
        from .tasks import Store as Tasks
        for tid in d['task_refs']:Tasks(self.fs).get(tid)
    def create(self,payload):
        from .project import ensure_writable
        require(isinstance(payload,dict),'invalid_decision','Payload de decisão inválido.')
        require(not(set(payload)-PROPOSAL_FIELDS-{'id','status'}),'managed_decision_fields','Criação não aceita aprovação, identidade de aprovador ou histórico.')
        require(payload.get('status','pending')=='pending','invalid_initial_state','Decisão nova começa pendente; aprovação é operação separada.',5)
        ensure_writable(self.fs)
        with metadata_lock(self.fs):
            ensure_writable(self.fs)
            d={'schema_version':2,'id':new_id('DEC'),'type':'other','status':'pending','subject_ref':None,'subject_sha256':None,'subject_manifest':[],'task_refs':[],'options':[],'recommended_option':None,'selected_option':None,'feedback':[],'authority_ref':None,'created_at':now(),'updated_at':now(),'decided_at':None,'revision':1,'history':[],'legacy_record':None,**payload}
            self._bind(d);check(d);self._task_refs(d)
            path=f'.omnx/decisions/{d["id"]}.json';raw=json_bytes(d);self.fs.write(path,raw,None)
        return result('Proposta registrada, sem autorizar execução.',changed_paths=[path],decision=d,sha256=digest(raw))
    def _write(self,path,old,nd,expected,action):
        require(len(old['history'])<200,'history_limit','Histórico cheio; crie uma nova decisão relacionada.',6)
        nd['history']=old['history']+[{'previous':state(old),'sha256':object_digest(state(old)),'action':action,'recorded_at':now()}]
        nd['revision']=old['revision']+1;nd['updated_at']=now();check(nd)
        raw=json_bytes(nd);self.fs.write(path,raw,expected)
        return result('Decisão registrada para a revisão exibida. Sem execução ou publicação.',changed_paths=[path],decision=nd,sha256=digest(raw))
    def update(self,did,expected,*,status=None,selected_option=None,feedback=None,authority_ref=None):
        from .project import ensure_writable
        ensure_writable(self.fs)
        with metadata_lock(self.fs):
            ensure_writable(self.fs);path,d,actual=self.read_record(did)
            require(actual==expected,'stale_state','A decisão mudou. Reabra e confira antes de agir.',3)
            require(d['schema_version']==2,'legacy_decision','Decisão v1 não é confiável para aprovação. Use decision revise e reconfirme.',5)
            if d['status'] in TERMINAL:
                require(status=='superseded' and selected_option is None and feedback is None and d['status']!='superseded','decision_terminal','Decisão encerrada é imutável; proponha outra revisão.',3)
            require(status is not None or feedback is not None,'empty_update','Nenhuma operação de decisão foi solicitada.')
            require(status in (None,'approved','rejected','changes_requested','superseded','cancelled'),'invalid_decision_status','Use revise para apresentar uma nova proposta pendente.')
            if selected_option is not None:require(status=='approved','choice_without_approval','Escolha só é gravada junto à aprovação.',5)
            if status in ('approved','rejected'):
                require(d['status']=='pending','revision_required','Pedido de alteração exige proposta revisada antes de nova decisão.',3)
            nd=deepcopy(d)
            if feedback is not None:
                require(isinstance(feedback,str) and bool(feedback.strip()) and len(feedback)<=4096,'invalid_feedback','Feedback precisa conter até 4096 caracteres.')
                nd['feedback'].append(feedback.strip())
            if status=='changes_requested':require(feedback is not None,'missing_feedback','Descreva o ajuste solicitado.')
            if status is not None:
                if status in TERMINAL:
                    require(isinstance(authority_ref,str) and bool(authority_ref.strip()),'missing_authority','Registre a origem da decisão.',5)
                    nd['authority_ref']=authority_ref.strip();nd['decided_at']=now()
                nd['status']=status
            if status=='approved':
                nd['selected_option']=selected_option
                if d['options']:
                    # One explicit option still must be chosen; no silent default.
                    require(selected_option in {x['id'] for x in d['options']},'missing_option','Escolha uma opção antes de aprovar.',5)
                if d['subject_ref']:
                    require(bundle_manifest(self.fs,d['subject_ref'])==d['subject_manifest'],'stale_subject','A proposta ou seus recursos mudaram. Solicite nova revisão.',3)
            action={None:'feedback','approved':'approve','rejected':'reject','changes_requested':'request_changes','superseded':'supersede','cancelled':'cancel'}[status]
            return self._write(path,d,nd,expected,action)
    def revise(self,did,expected,patch):
        from .project import ensure_writable
        require(isinstance(patch,dict) and not(set(patch)-PROPOSAL_FIELDS),'managed_decision_fields','Revisão altera apenas campos da proposta.')
        ensure_writable(self.fs)
        with metadata_lock(self.fs):
            ensure_writable(self.fs);path,d,actual=self.read_record(did)
            require(actual==expected,'stale_state','A decisão mudou; releia.',3)
            require(d['schema_version']==1 or d['status'] in ('pending','changes_requested'),'decision_terminal','Decisão encerrada exige nova proposta, sem reescrever a aprovação.',3)
            if d['schema_version']==1:
                # Explicit migration preserves original bytes' digest + data and
                # withdraws its unsafe approval from active use.
                legacy=deepcopy(d)
                d={**d,'schema_version':2,'revision':1,'status':'pending','selected_option':None,'authority_ref':None,'decided_at':None,'history':[],'legacy_record':{'sha256':actual,'data':legacy},'subject_manifest':[]}
                d['subject_sha256']=None
                nd={**d,**patch,'updated_at':now()};self._bind(nd);check(nd);self._task_refs(nd)
                raw=json_bytes(nd);self.fs.write(path,raw,expected)
                return result('Decisão legada preservada e reapresentada como pendente; aprovação antiga não foi herdada.',changed_paths=[path],decision=nd,sha256=digest(raw))
            nd={**deepcopy(d),**patch,'status':'pending','selected_option':None,'authority_ref':None,'decided_at':None}
            # A new proposal explicitly captures current assets; callers may pin
            # a digest in patch to require a specific main file.
            if 'subject_sha256' not in patch:nd['subject_sha256']=None
            self._bind(nd);check({**nd,'history':d['history']});self._task_refs(nd)
            return self._write(path,d,nd,expected,'revise')
