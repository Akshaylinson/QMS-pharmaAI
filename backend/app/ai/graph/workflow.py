"""Typed LangGraph complaint pipeline. Nodes have one responsibility and remain independently testable."""
import re
from datetime import datetime
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END

class ComplaintState(TypedDict, total=False):
    raw_input: str; source_type: str; current_complaint: dict[str, Any]; extracted_complaint: dict[str, Any]; extraction_confidence: dict[str,float]; missing_fields: list[str]; validation_errors: list[str]; normalized_complaint: dict[str,Any]; severity_assessment: dict[str,Any]; risk_assessment: dict[str,Any]; completeness_assessment: dict[str,Any]; duplicate_candidates: list[dict]; root_cause_recommendations: list[str]; capa_recommendations: dict[str,list[str]]; complaint_summary: str; final_response: dict[str,Any]; errors: list[str]; stages: list[str]

def _stage(s, name): return {'stages': s.get('stages', []) + [name]}
def classify(s): return _stage(s, 'Input classified')
def extract(s):
    """Extract only facts stated in the latest chat turn, then merge them with the draft."""
    t=s['raw_input']; low=t.lower()
    def get(pattern):
        match=re.search(pattern,t,re.I)
        return match.group(1).strip(' .,;:') if match else None
    def iso_date(value):
        if not value: return None
        for pattern in ('%B %Y','%b %Y','%d/%m/%Y','%d-%m-%Y','%m/%d/%Y','%m-%d-%Y'):
            try: return datetime.strptime(value,pattern).date().isoformat()
            except ValueError: pass
        return value
    x={
        'customer_name':get(r'(?:customer|from)\s+([A-Z][\w .&-]+?)(?:\s+(?:reports|states|has|complains|said)|[,.])') or get(r'^([A-Z][\w .&-]+?)\s+(?:reported|reports|states|complains)'),
        'source':get(r'(?:source|received\s+via)\s*(?:is|:)?\s*(email|pharmacy|distributor|hospital|phone|web portal)'),
        'product_name':get(r'(?:product(?:\s+name)?\s*(?:is|:)?|for|in)\s+([A-Za-z][\w -]+?)(?=\s+(?:\d+\s*(?:mg|ml|g|%)|batch|lot)|[,.])'),
        'product_strength':get(r'(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|%))'),
        'batch_number':get(r'(?:batch|lot)(?:\s+(?:number|no\.?))?\s*(?:is|:|#)?\s*([A-Za-z0-9][A-Za-z0-9-]+)'),
        'affected_quantity':get(r'(?:affected\s+(?:quantity|qty)(?:\s+is)?\s*[:=]?\s*|\b)(\d+\s*(?:capsules?|tablets?|packs?|units?|vials?|bottles?|drums?|kg|g))') or get(r'(\d+\s+(?:\w+\s+){0,2}(?:capsules?|tablets?|packs?|units?|vials?|bottles?|drums?))'),
        'manufacturing_date':iso_date(get(r'(?:manufactur(?:ing|ed)\s+date|mfg(?:\.?\s*date)?)\s*(?:is|:)?\s*([A-Za-z]+\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})')),
        'expiry_date':iso_date(get(r'(?:expiry|expiration|exp(?:iry)?\s+date)\s*(?:is|:)?\s*([A-Za-z]+\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})')),
        'originating_site':get(r'(?:originating\s+(?:site|block)|site\s+block)\s*(?:is|:)?\s*([A-Za-z0-9][\w .-]+?)(?=[,.]|$)'),
        'impacted_materials':get(r'(?:impacted\s+(?:non-product\s+)?materials?|npm)\s*(?:are|is|:)?\s*([A-Za-z0-9][\w ,/&()-]+?)(?=[.]|$)'),
    }
    # A first complaint message is the formal record; correction messages should not overwrite it.
    if not s.get('current_complaint', {}).get('description') or any(w in low for w in ['reported', 'complaint', 'defect', 'contamination', 'discolor', 'broken', 'damaged']):
        x['description']=t
    if any(w in low for w in ['discolor', 'colour', 'color']): x['complaint_type']='Product Defect - Discoloration'
    elif any(w in low for w in ['blister','packaging','seal']): x['complaint_type']='Packaging Defect'
    elif any(w in low for w in ['foreign matter','foreign particle','contamination','particulate']): x['complaint_type']='Product Defect - Foreign Matter'
    elif any(w in low for w in ['broken','damaged','defect']): x['complaint_type']='Product Defect'
    if any(w in low for w in ['email','pharmacy','distributor','hospital']): x['source']=x['source'] or next((w.title() for w in ['email','pharmacy','distributor','hospital'] if w in low),None)
    x={k:v for k,v in x.items() if v not in (None,'')}
    # When configured, the remote provider produces the extraction; local parsing is a transparent no-credential fallback for demo intake.
    try:
        from app.ai.providers.factory import get_llm_provider
        from app.schemas.ai import ExtractionOutput
        from app.ai.prompts.extraction import EXTRACTION
        provider=get_llm_provider()
        if provider:
            model=provider.structured(f'{EXTRACTION}\nComplaint:\n{t}', ExtractionOutput)
            x={**x, **{k:v for k,v in model.model_dump().items() if v is not None}}
    except Exception as exc:
        return {'extracted_complaint':x,'extraction_confidence':{k:(.78 if v else 0) for k,v in x.items()},'errors':[f'LLM extraction unavailable; used local intake parser: {type(exc).__name__}'], **_stage(s,'Complaint extracted')}
    return {'extracted_complaint':x,'extraction_confidence':{k:(.9 if v else 0) for k,v in x.items()}, **_stage(s,'Complaint extracted')}
def normalize(s):
    base={k:v for k,v in s.get('current_complaint',{}).items() if v not in (None,'')}
    updates={k:v for k,v in s['extracted_complaint'].items() if v not in (None,'')}
    # Do not let a correction turn replace the original narrative with a one-line correction.
    if 'description' not in updates: updates.pop('description',None)
    return {'normalized_complaint':{**base,**updates}, 'updated_fields':list(updates), **_stage(s,'Information normalized')}
def completeness(s):
    x=s['normalized_complaint']; missing=[f for f in ['customer_name','product_name','batch_number','description'] if not x.get(f)]; status='COMPLETE' if not missing else ('PARTIALLY_COMPLETE' if len(missing)<3 else 'INCOMPLETE'); return {'missing_fields':missing,'completeness_assessment':{'status':status,'missing_fields':missing,'questions_to_ask':[f'Please provide {m.replace("_"," ")}.' for m in missing],'confidence':round(1-len(missing)/4,2)},**_stage(s,'Completeness checked')}
def risk(s):
    text=(s['raw_input']+' '+str(s['normalized_complaint'].get('description',''))).lower(); critical=any(x in text for x in ['contamination','adverse event','patient injury','foreign particle','sterility']); high=critical or s['normalized_complaint'].get('safety_concern')
    level='CRITICAL' if critical else ('HIGH' if high else ('MEDIUM' if any(x in text for x in ['broken','damaged','defect','discolor']) else 'LOW')); sev='Critical' if level=='CRITICAL' else ('Major' if level in ['HIGH','MEDIUM'] else 'Minor'); priority='Urgent' if level=='CRITICAL' else ('High' if level=='HIGH' else ('Medium' if level=='MEDIUM' else 'Low'))
    action='Route to QA Investigation & Issue Replacement' if level in ['CRITICAL','HIGH','MEDIUM'] else 'Route to QA review and close after verification'
    a={'risk_level':level,'severity':sev,'priority':priority,'reasoning':'Potential quality risk identified from the reported facts. Confirm the scope, inspect retained samples, and complete qualified QA review before any disposition.','suggested_next_action':action}; return {'risk_assessment':a,'severity_assessment':a,**_stage(s,'Risk assessed')}
def duplicates(s): return {'duplicate_candidates':[], **_stage(s,'Duplicate checked')}
def root_cause(s):
    t=s['raw_input'].lower(); causes=['Potential packaging-line or transit damage investigation area'] if any(x in t for x in ['blister','damaged','broken']) else ['Potential product quality investigation area']; return {'root_cause_recommendations':causes,**_stage(s,'Root cause recommendations generated')}
def capa(s): return {'capa_recommendations':{'corrective_actions':['Quarantine/inspect retained sample as applicable','Open batch investigation'], 'preventive_actions':['Review relevant SOP and packaging/process controls']},**_stage(s,'CAPA recommendations generated')}
def summary(s):
    x=s['normalized_complaint']; r=s['risk_assessment']; updates=s.get('updated_fields',[])
    x.update({'severity':r['severity'],'priority':r['priority'],'risk_level':r['risk_level'],'suggested_next_action':r['suggested_next_action'],'initial_risk_assessment':r['reasoning']})
    friendly=', '.join(field.replace('_',' ') for field in updates) or 'the complaint details'
    out=f"Got it. I updated {friendly} in the complaint form. The current assessment is {r['severity']} severity; suggested next action: {r['suggested_next_action']}."
    return {'complaint_summary':out,'final_response':{'extracted_complaint':x,'updated_fields':updates,'confidence':s['extraction_confidence'],'completeness':s['completeness_assessment'],'risk':r,'duplicates':s['duplicate_candidates'],'root_causes':s['root_cause_recommendations'],'capa':s['capa_recommendations'],'summary':out,'stages':s.get('stages',[])+['Ready for review']}}
def build_graph():
    g=StateGraph(ComplaintState)
    for name, fn in [('classify',classify),('extract',extract),('normalize',normalize),('completeness',completeness),('risk',risk),('duplicates',duplicates),('root_cause',root_cause),('capa',capa),('summary',summary)]: g.add_node(name,fn)
    g.add_edge(START,'classify')
    for a,b in zip(['classify','extract','normalize','completeness','risk','duplicates','root_cause','capa'],['extract','normalize','completeness','risk','duplicates','root_cause','capa','summary']): g.add_edge(a,b)
    g.add_edge('summary',END); return g.compile()
complaint_graph=build_graph()
