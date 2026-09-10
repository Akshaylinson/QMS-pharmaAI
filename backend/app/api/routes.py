from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.complaint import Complaint, AnalysisRecord, AuditLog
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate, ComplaintOut, IntakeRequest, CopilotRequest
from app.ai.graph.workflow import complaint_graph
from app.documents.extractor import extract_document
router=APIRouter()
def number(): return f"CC-{datetime.utcnow():%Y%m%d}-{datetime.utcnow().microsecond:06d}"
def record(db,cid,kind,payload): db.add(AnalysisRecord(complaint_id=cid,analysis_type=kind,payload=payload,provider='langgraph'))
def duplicate_matches(db, complaint):
    """Deterministic persisted-data comparison; deliberately returns candidates for QA review, never a decision."""
    if not complaint.batch_number and not complaint.product_name: return []
    candidates=db.scalars(select(Complaint).where(Complaint.id != complaint.id)).all(); out=[]
    for other in candidates:
        score=0
        if complaint.batch_number and complaint.batch_number==other.batch_number: score+=.55
        if complaint.product_name and complaint.product_name==other.product_name: score+=.3
        if complaint.customer_name and complaint.customer_name==other.customer_name: score+=.15
        if score>=.55: out.append({'complaint_id':other.id,'complaint_number':other.complaint_number,'similarity_score':round(score,2),'reason':'Matching batch/product/customer fields; requires QA review.'})
    return sorted(out,key=lambda x:x['similarity_score'],reverse=True)
@router.post('/complaints',response_model=ComplaintOut,status_code=201)
def create(body: ComplaintCreate, db:Session=Depends(get_db)):
    c=Complaint(complaint_number=number(),**body.model_dump()); db.add(c); db.flush(); db.add(AuditLog(complaint_id=c.id,action='Complaint created',details={})); db.commit(); db.refresh(c); return c
@router.get('/complaints',response_model=list[ComplaintOut])
def list_complaints(status:str|None=None, q:str|None=None, db:Session=Depends(get_db)):
    stmt=select(Complaint).order_by(Complaint.created_at.desc())
    if status: stmt=stmt.where(Complaint.status==status)
    if q: stmt=stmt.where((Complaint.customer_name.ilike(f'%{q}%'))|(Complaint.product_name.ilike(f'%{q}%'))|(Complaint.complaint_number.ilike(f'%{q}%')))
    return db.scalars(stmt).all()
@router.get('/complaints/{complaint_id}',response_model=ComplaintOut)
def get_complaint(complaint_id:str,db:Session=Depends(get_db)):
    c=db.get(Complaint,complaint_id)
    if not c: raise HTTPException(404,'Complaint not found')
    return c
@router.put('/complaints/{complaint_id}',response_model=ComplaintOut)
def update(complaint_id:str,body:ComplaintUpdate,db:Session=Depends(get_db)):
    c=db.get(Complaint,complaint_id)
    if not c: raise HTTPException(404,'Complaint not found')
    for k,v in body.model_dump(exclude_unset=True).items(): setattr(c,k,v)
    db.add(AuditLog(complaint_id=c.id,action='Complaint updated',details={})); db.commit(); db.refresh(c); return c
@router.delete('/complaints/{complaint_id}',status_code=204)
def delete(complaint_id:str,db:Session=Depends(get_db)):
    c=db.get(Complaint,complaint_id)
    if not c: raise HTTPException(404,'Complaint not found')
    db.delete(c); db.commit()
@router.post('/complaints/intake')
def intake(body:IntakeRequest):
    return complaint_graph.invoke({'raw_input':body.raw_input,'source_type':body.source_type,'current_complaint':body.current_complaint,'stages':[]})['final_response']
@router.post('/documents/extract')
async def document_extract(file:UploadFile=File(...)):
    try:
        text=extract_document(file.filename or '',await file.read())
        return {'filename':file.filename,'text':text,'characters':len(text)}
    except ValueError as e: raise HTTPException(422,str(e))
@router.post('/complaints/{complaint_id}/analyze')
def analyze(complaint_id:str,db:Session=Depends(get_db)):
    c=db.get(Complaint,complaint_id)
    if not c: raise HTTPException(404,'Complaint not found')
    result=complaint_graph.invoke({'raw_input':c.description or '', 'source_type':c.source or 'manual','stages':[]})['final_response']; result['duplicates']=duplicate_matches(db,c); r=result['risk']; c.severity=r['severity'];c.priority=r['priority'];c.risk_level=r['risk_level']; record(db,c.id,'full_analysis',result);db.add(AuditLog(complaint_id=c.id,action='AI analysis completed',details={'risk':r['risk_level']}));db.commit();return result
@router.post('/complaints/{complaint_id}/{operation}')
def operation(complaint_id:str,operation:str,db:Session=Depends(get_db)):
    if operation not in {'risk-assessment','duplicate-check','root-cause','capa','summary'}: raise HTTPException(404,'Operation not found')
    c=db.get(Complaint,complaint_id)
    if not c: raise HTTPException(404,'Complaint not found')
    result=complaint_graph.invoke({'raw_input':c.description or '', 'source_type':c.source or 'manual','stages':[]})['final_response']; result['duplicates']=duplicate_matches(db,c); key={'risk-assessment':'risk','duplicate-check':'duplicates','root-cause':'root_causes','capa':'capa','summary':'summary'}[operation]; record(db,c.id,operation,{key:result[key]});db.commit();return {key:result[key]}
@router.post('/ai/copilot')
def copilot(body:CopilotRequest):
    c=body.complaint; q=body.question.lower(); missing=[x for x in ['customer_name','product_name','batch_number','description'] if not c.get(x)]
    if 'missing' in q: answer='Missing information: '+(', '.join(missing) if missing else 'none of the core intake fields.')
    elif any(w in q for w in ['root cause','investigator']): answer='AI Recommendation: inspect retained samples, batch records, and relevant packaging/process controls. This is not a confirmed root cause.'
    elif 'capa' in q: answer='AI Recommendation: open a controlled investigation, inspect impacted batch/retains, and review applicable SOP controls.'
    elif 'summar' in q: answer=f"{c.get('customer_name') or 'Customer'} reported {c.get('complaint_type') or 'a complaint'} for {c.get('product_name') or 'an unspecified product'}; batch {c.get('batch_number') or 'not provided'}."
    else: answer='Insufficient information in the complaint.'
    return {'answer':answer,'requires_human_review':True}
@router.get('/settings/info')
def settings_info():
    from app.core.config import settings
    return {
        'llm_provider': settings.llm_provider,
        'groq_model': settings.groq_model,
        'gemini_model': settings.gemini_model,
        'groq_configured': bool(settings.groq_api_key),
        'gemini_configured': bool(settings.gemini_api_key),
        'database_url': settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database_url,
        'frontend_origin': settings.frontend_origin,
        'version': '1.0.0',
        'app_name': 'AIVOA.AI — Pharmaceutical QMS',
    }


def stats(db:Session=Depends(get_db)):
    cs=db.scalars(select(Complaint)).all(); counts=lambda field:{v:sum(1 for c in cs if getattr(c,field)==v) for v in set(getattr(c,field) for c in cs if getattr(c,field))}; return {'total':len(cs),'open':sum(c.status!='RESOLVED' for c in cs),'high_risk':sum(c.risk_level in ['HIGH','CRITICAL'] for c in cs),'critical':sum(c.risk_level=='CRITICAL' for c in cs),'pending_review':sum(c.status=='PENDING_REVIEW' for c in cs),'resolved':sum(c.status=='RESOLVED' for c in cs),'by_severity':counts('severity'),'by_status':counts('status'),'recent':[ComplaintOut.model_validate(c).model_dump(mode='json') for c in cs[:8]]}

@router.get('/dashboard/analytics')
def analytics(db:Session=Depends(get_db)):
    from collections import defaultdict
    def norm(v): return v.strip().title() if isinstance(v,str) else v
    cs=db.scalars(select(Complaint).order_by(Complaint.created_at)).all()
    by_date=defaultdict(int)
    for c in cs: by_date[c.created_at.strftime('%Y-%m-%d')]+=1
    complaints_over_time=[{'date':d,'count':v} for d,v in sorted(by_date.items())]
    by_month=defaultdict(int)
    for c in cs: by_month[c.created_at.strftime('%b %Y')]+=1
    complaints_by_month=[{'month':m,'count':v} for m,v in sorted(by_month.items(),key=lambda x:x[0])]
    by_sev=defaultdict(int)
    for c in cs:
        if c.severity: by_sev[norm(c.severity)]+=1
    sev_order=['Critical','Major','Minor']
    severity_breakdown=[{'severity':k,'count':v} for k,v in sorted(by_sev.items(),key=lambda x:sev_order.index(x[0]) if x[0] in sev_order else 99)]
    by_risk=defaultdict(int)
    for c in cs:
        if c.risk_level: by_risk[norm(c.risk_level)]+=1
    risk_order=['Critical','High','Medium','Low']
    risk_breakdown=[{'risk':k,'count':v} for k,v in sorted(by_risk.items(),key=lambda x:risk_order.index(x[0]) if x[0] in risk_order else 99)]
    by_status=defaultdict(int)
    for c in cs:
        if c.status: by_status[norm(c.status.replace('_',' '))]+=1
    status_breakdown=[{'status':k,'count':v} for k,v in sorted(by_status.items(),key=lambda x:-x[1])]
    by_customer=defaultdict(int)
    for c in cs:
        if c.customer_name: by_customer[norm(c.customer_name)]+=1
    top_customers=[{'customer':k,'count':v} for k,v in sorted(by_customer.items(),key=lambda x:-x[1])[:10]]
    by_product=defaultdict(int)
    for c in cs:
        if c.product_name: by_product[norm(c.product_name)]+=1
    top_products=[{'product':k,'count':v} for k,v in sorted(by_product.items(),key=lambda x:-x[1])[:10]]
    by_type=defaultdict(int)
    for c in cs:
        if c.complaint_type: by_type[norm(c.complaint_type)]+=1
    complaint_types=[{'type':k,'count':v} for k,v in sorted(by_type.items(),key=lambda x:-x[1])[:10]]
    sev_month=defaultdict(lambda:defaultdict(int))
    for c in cs:
        if c.severity: sev_month[c.created_at.strftime('%b %Y')][norm(c.severity)]+=1
    severity_over_time=[{'month':m,**sevs} for m,sevs in sorted(sev_month.items(),key=lambda x:x[0])]
    by_source=defaultdict(int)
    for c in cs:
        if c.source: by_source[norm(c.source)]+=1
    source_breakdown=[{'source':k,'count':v} for k,v in sorted(by_source.items(),key=lambda x:-x[1])]
    return {'complaints_over_time':complaints_over_time,'complaints_by_month':complaints_by_month,'severity_breakdown':severity_breakdown,'risk_breakdown':risk_breakdown,'status_breakdown':status_breakdown,'top_customers':top_customers,'top_products':top_products,'complaint_types':complaint_types,'severity_over_time':severity_over_time,'source_breakdown':source_breakdown}
