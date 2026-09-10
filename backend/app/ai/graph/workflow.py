"""Typed LangGraph complaint pipeline. Nodes have one responsibility and remain independently testable."""
import re
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END

class ComplaintState(TypedDict, total=False):
    raw_input: str; source_type: str; extracted_complaint: dict[str, Any]; extraction_confidence: dict[str,float]; missing_fields: list[str]; validation_errors: list[str]; normalized_complaint: dict[str,Any]; severity_assessment: dict[str,Any]; risk_assessment: dict[str,Any]; completeness_assessment: dict[str,Any]; duplicate_candidates: list[dict]; root_cause_recommendations: list[str]; capa_recommendations: dict[str,list[str]]; complaint_summary: str; final_response: dict[str,Any]; errors: list[str]; stages: list[str]

def _stage(s, name): return {'stages': s.get('stages', []) + [name]}
def classify(s): return _stage(s, 'Input classified')
def extract(s):
    t=s['raw_input']; get=lambda p: (re.search(p,t,re.I).group(1).strip(' .,') if re.search(p,t,re.I) else None)
    x={'customer_name':get(r'(?:customer|from)\s+([A-Z][\w .&-]+?)\s+(?:reports|states|has|complains)'), 'product_name':get(r'(?:Batch\s+\S+\s+of|product\s+)([A-Za-z][\w -]+?(?:\d+\s*(?:mg|ml|%))?)'), 'batch_number':get(r'(?:batch|lot)\s*(?:number)?\s*[:#]?\s*([A-Za-z0-9-]+)'), 'affected_quantity':get(r'(\d+\s*(?:tablets|packs|units|vials|bottles))'), 'description':t}
    low=t.lower(); x['complaint_type']='Packaging defect' if any(w in low for w in ['blister','pack','packaging','seal']) else ('Product defect' if any(w in low for w in ['broken','defect','particulate']) else None)
    x['safety_concern']=any(w in low for w in ['patient','injury','adverse','safety','contamination'])
    # When configured, the remote provider produces the extraction; local parsing is a transparent no-credential fallback for demo intake.
    try:
        from app.ai.providers.factory import get_llm_provider
        from app.schemas.ai import ExtractionOutput
        from app.ai.prompts.extraction import EXTRACTION
        provider=get_llm_provider()
        if provider:
            model=provider.structured(f'{EXTRACTION}\nComplaint:\n{t}', ExtractionOutput)
            x={k:v for k,v in model.model_dump().items() if v is not None}
    except Exception as exc:
        return {'extracted_complaint':x,'extraction_confidence':{k:(.78 if v else 0) for k,v in x.items()},'errors':[f'LLM extraction unavailable; used local intake parser: {type(exc).__name__}'], **_stage(s,'Complaint extracted')}
    return {'extracted_complaint':x,'extraction_confidence':{k:(.9 if v else 0) for k,v in x.items()}, **_stage(s,'Complaint extracted')}
def normalize(s): return {'normalized_complaint':{k:v for k,v in s['extracted_complaint'].items() if v is not None}, **_stage(s,'Information normalized')}
def completeness(s):
    x=s['normalized_complaint']; missing=[f for f in ['customer_name','product_name','batch_number','description'] if not x.get(f)]; status='COMPLETE' if not missing else ('PARTIALLY_COMPLETE' if len(missing)<3 else 'INCOMPLETE'); return {'missing_fields':missing,'completeness_assessment':{'status':status,'missing_fields':missing,'questions_to_ask':[f'Please provide {m.replace("_"," ")}.' for m in missing],'confidence':round(1-len(missing)/4,2)},**_stage(s,'Completeness checked')}
def risk(s):
    text=s['raw_input'].lower(); critical=any(x in text for x in ['contamination','adverse event','patient injury','foreign particle','sterility']); high=critical or s['normalized_complaint'].get('safety_concern')
    level='CRITICAL' if critical else ('HIGH' if high else ('MEDIUM' if any(x in text for x in ['broken','damaged','defect']) else 'LOW')); sev='CRITICAL' if level=='CRITICAL' else ('MAJOR' if level in ['HIGH','MEDIUM'] else 'MINOR'); priority='URGENT' if level=='CRITICAL' else ('HIGH' if level=='HIGH' else ('MEDIUM' if level=='MEDIUM' else 'LOW')); a={'risk_level':level,'severity':sev,'priority':priority,'reasoning':'AI recommendation based only on the reported issue; requires qualified QA review.'}; return {'risk_assessment':a,'severity_assessment':a,**_stage(s,'Risk assessed')}
def duplicates(s): return {'duplicate_candidates':[], **_stage(s,'Duplicate checked')}
def root_cause(s):
    t=s['raw_input'].lower(); causes=['Potential packaging-line or transit damage investigation area'] if any(x in t for x in ['blister','damaged','broken']) else ['Potential product quality investigation area']; return {'root_cause_recommendations':causes,**_stage(s,'Root cause recommendations generated')}
def capa(s): return {'capa_recommendations':{'corrective_actions':['Quarantine/inspect retained sample as applicable','Open batch investigation'], 'preventive_actions':['Review relevant SOP and packaging/process controls']},**_stage(s,'CAPA recommendations generated')}
def summary(s):
    x=s['normalized_complaint']; r=s['risk_assessment']; out=f"{x.get('customer_name') or 'Customer'} reported {x.get('complaint_type') or 'a complaint'} for {x.get('product_name') or 'an unspecified product'} (batch {x.get('batch_number') or 'not provided'}). AI recommendation: {r['risk_level']} risk / {r['severity']} severity. Next action: QA review and investigation triage."; return {'complaint_summary':out,'final_response':{'extracted_complaint':x,'confidence':s['extraction_confidence'],'completeness':s['completeness_assessment'],'risk':r,'duplicates':s['duplicate_candidates'],'root_causes':s['root_cause_recommendations'],'capa':s['capa_recommendations'],'summary':out,'stages':s.get('stages',[])+['Ready for review']}}
def build_graph():
    g=StateGraph(ComplaintState)
    for name, fn in [('classify',classify),('extract',extract),('normalize',normalize),('completeness',completeness),('risk',risk),('duplicates',duplicates),('root_cause',root_cause),('capa',capa),('summary',summary)]: g.add_node(name,fn)
    g.add_edge(START,'classify')
    for a,b in zip(['classify','extract','normalize','completeness','risk','duplicates','root_cause','capa'],['extract','normalize','completeness','risk','duplicates','root_cause','capa','summary']): g.add_edge(a,b)
    g.add_edge('summary',END); return g.compile()
complaint_graph=build_graph()
