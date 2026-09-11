"""Typed LangGraph complaint pipeline. Nodes have one responsibility and remain independently testable."""
import re
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END

class ComplaintState(TypedDict, total=False):
    raw_input: str; source_type: str; current_complaint: dict[str, Any]; extracted_complaint: dict[str, Any]; extraction_confidence: dict[str,float]; missing_fields: list[str]; validation_errors: list[str]; normalized_complaint: dict[str,Any]; severity_assessment: dict[str,Any]; risk_assessment: dict[str,Any]; completeness_assessment: dict[str,Any]; duplicate_candidates: list[dict]; root_cause_recommendations: list[str]; capa_recommendations: dict[str,list[str]]; complaint_summary: str; final_response: dict[str,Any]; errors: list[str]; stages: list[str]

def _stage(s, name): return {'stages': s.get('stages', []) + [name]}
def classify(s): return _stage(s, 'Input classified')
def extract(s):
    """LLM is the primary extractor. Regex is a zero-dependency fallback only."""
    t=s['raw_input']; low=t.lower()
    def explicit_field_updates():
        """Map a named form parameter to its value without interpreting it.

        This path is deliberately run before AI extraction for chat corrections.
        It means e.g. "set manufacturing date to batch cleared after rework" is
        saved verbatim instead of being rejected or guessed as a date.
        """
        aliases={
            'source': ('complaint source', 'source'),
            'customer_name': ('customer name',),
            'product_name': ('product name',),
            'product_strength': ('product strength', 'strength', 'grade'),
            'batch_number': ('batch / lot number', 'batch number', 'lot number', 'batch', 'lot'),
            'affected_quantity': ('affected quantity', 'affected qty', 'quantity'),
            'manufacturing_date': ('manufacturing date', 'manufacturing', 'mfg date', 'mfg'),
            'expiry_date': ('expiry date', 'expiration date', 'expiry', 'expiration', 'exp date'),
            'originating_site': ('originating site block', 'originating site', 'site block'),
            'impacted_materials': ('impacted non-product materials', 'impacted materials', 'material impact'),
            'complaint_type': ('complaint category', 'complaint type', 'category'),
            'description': ('complaint description', 'description'),
        }
        updates={}
        for field, names in aliases.items():
            # This shortcut is only for an actual change command or a labelled
            # value at the beginning of a line.  A complaint narrative can
            # naturally say "for batch ABC-123, manufactured ..."; treating
            # that as a field command would incorrectly assign the rest of the
            # paragraph to batch_number and bypass structured AI extraction.
            # Values remain deliberately unconstrained once the intent is
            # unambiguous, so QA-provided free-form values are still preserved.
            joined='|'.join(re.escape(name) for name in sorted(names,key=len,reverse=True))
            match=re.search(
                rf'\b(?:change|update|set|add)\s+(?:{joined})\s*(?:as|is|to|should be|=|:|-)?\s*(.+?)(?:\n|$)',
                t,
                re.I,
            )
            if not match:
                match=re.search(
                    rf'(?:^|\n)\s*(?:{joined})\s*(?:=|:|-)\s*(.+?)(?:\n|$)',
                    t,
                    re.I,
                )
            if match:
                value=match.group(1).strip()
                if value:
                    updates[field]=value
        return updates

    direct_updates=explicit_field_updates()
    if direct_updates and len(t.split()) <= 120:
        return {'extracted_complaint':direct_updates,'extraction_confidence':{k:.99 for k in direct_updates}, **_stage(s,'Named fields updated')}
    # --- Primary path: LLM extraction ---
    try:
        from app.ai.providers.factory import get_llm_provider
        from app.schemas.ai import ExtractionOutput
        from app.ai.prompts.extraction import EXTRACTION
        provider=get_llm_provider()
        if provider:
            # Pass current form state so LLM knows what's already filled
            current=s.get('current_complaint',{})
            context_hint=''
            if current:
                filled=[f"{k}: {v}" for k,v in current.items() if v and k not in ('severity','priority','risk_level','suggested_next_action','initial_risk_assessment','status')]
                if filled: context_hint='\n\nAlready filled (only overwrite if the new text explicitly instructs a change to that field):\n'+'; '.join(filled)
            model=provider.structured(f'{EXTRACTION}{context_hint}\n\nText to extract from:\n{t}', ExtractionOutput)
            x={k:v for k,v in model.model_dump().items() if v is not None}
            return {'extracted_complaint':x,'extraction_confidence':{k:.92 for k in x}, **_stage(s,'Complaint extracted')}
    except Exception:
        pass  # fall through to regex fallback
    # --- Fallback path: regex (no LLM credentials) ---
    def get(pattern):
        m=re.search(pattern,t,re.I)
        return m.group(1).strip(' .,;:') if m else None
    x={
        'source': get(r'(?:source\s*[:\-]\s*)(email|phone|portal|fax)') or ('Email' if 'email' in low else None),
        'customer_name': get(r'(?:^|\n)From:\s*([^\n<]+?)(?:\s*[<,\n]|$)') or get(r'(?:yours\s+(?:faithfully|sincerely|truly)|regards|sincerely)[,\s]+([A-Z][\w .&-]+?)(?:\n|$)') or get(r'(?:customer|reported by|submitted by)\s*[:\-]\s*([A-Z][\w .&-]+?)(?:[,\n]|$)') or get(r'^(.*?)\s+(?:had|reported|submitted|raised)\s+(?:a\s+)?complaint\b'),
        # Do not use a broad "anything before inhaler" expression here: in
        # lower-case narrative text it can swallow prose such as "complaint
        # regarding their recent purchase of".  Anchor product forms to an
        # explicit product context instead.
        'product_name': get(r'Product\s+Name\s*[:\-]\s*([^\n]+?)(?:\n|$)') or get(r'(?:purchase\s+of|product(?:\s+name)?\s*(?:is|:|\-)?|for)\s+([A-Za-z][A-Za-z0-9-]*(?:\s+[A-Za-z0-9-]+){0,5}\s+(?:Capsules?|Tablets?|Injection|Solution|Syrup|Cream|Ointment|Inhalers?))'),
        'product_strength': get(r'Strength\s*[:\-]\s*([\d.]+\s*(?:mg|mcg|g|ml|mL|%|IU)[^\n]*)') or get(r'([\d.]+\s*(?:mg|mcg|g|ml|mL|%|IU))'),
        # Prefer a full "batch number ... was VALUE" construction before the
        # shorter batch/lot form. This prevents the word "number" itself from
        # being recorded as a lot number.
        'batch_number': get(r'\b(?:batch|lot)\s+(?:number|no\.?)\b(?:\s+\w+){0,6}?\s+(?:was|is|:|#)\s*([A-Za-z0-9][A-Za-z0-9-]{2,})') or get(r'\b(?:batch|lot)\s*(?:[:#\-]\s*|\s+(?!(?:number|no\.?)\b))([A-Za-z0-9][A-Za-z0-9-]{2,})'),
        'affected_quantity': get(r'Affected\s+Qty\s*[:\-]\s*([^\n]+?)(?:\n|$)') or get(r'(?:up\s*to|upto)\s+(\d+\s+\w+)') or get(r'(\d+\s+(?:capsules?|tablets?|packs?|units?|vials?|bottles?|products?))'),
        'manufacturing_date': get(r'Manufacturing\s*(?:Date)?\s*[:\-]\s*([^\n]+)') or get(r'(?:manufactur(?:ing|ed)|produced)\s+(?:date\s+(?:as|is|:)?\s*)?(?:in\s+)?([A-Za-z]+\s+\d{4}|[^\n.]+)'),
        'expiry_date': get(r'(?:Expiry|Expiration)\s*(?:Date)?\s*[:\-]\s*([^\n]+)') or get(r'expir(?:y|ing|ation|ed|es)\s+(?:date\s+(?:as|is|:)?\s*)?(?:on\s+|in\s+)?([A-Za-z]+\s+\d{4}|[^\n.]+)'),
        'originating_site': get(r'(?:originating\s+site|site\s+block)\s*[:\-]\s*([A-Za-z0-9][\w .-]+?)(?=[,\n.]|$)') or get(r'originated\s+from\s+([A-Za-z0-9][\w .-]+?)(?=[,\n.]|$)'),
        'impacted_materials': get(r'((?:primary|secondary)\s+packaging\s+material[^.,]*)'),
    }
    # Retain any labelled values the generic patterns did not cover, rather
    # than requiring their values to match a preconceived format.
    x={**x,**{key:value for key,value in direct_updates.items() if value}}
    if not s.get('current_complaint',{}).get('description') or any(w in low for w in ['reported','complaint','defect','contamination','discolor','broken','damaged','foreign']):
        x['description']=t
    if any(w in low for w in ['email','phone','portal','fax']): x['source']=x.get('source') or next((w.title() for w in ['email','phone','portal','fax'] if w in low),None)
    if not x.get('complaint_type') and any(word in low for word in ['blister','damaged','broken','crushed','tube removed','tubes removed']):
        x['complaint_type']='Packaging Damage'
    x={k:v for k,v in x.items() if v not in (None,'')}
    return {'extracted_complaint':x,'extraction_confidence':{k:.72 for k in x},'errors':['LLM unavailable; used local regex fallback.'], **_stage(s,'Complaint extracted')}
def normalize(s):
    base={k:v for k,v in s.get('current_complaint',{}).items() if v not in (None,'')}
    # Only apply fields the LLM actually extracted (non-null) — never let a null overwrite a good value
    updates={k:v for k,v in s['extracted_complaint'].items() if v not in (None,'')}
    # Preserve the original description unless the new turn is a longer/richer narrative
    if 'description' in updates and base.get('description') and len(str(updates['description']))<len(str(base.get('description','')))*0.8:
        updates.pop('description')
    merged={**base,**updates}
    # Track only fields that actually changed from base
    changed=[k for k,v in updates.items() if str(base.get(k,''))!=str(v)]
    return {'normalized_complaint':merged,'updated_fields':changed, **_stage(s,'Information normalized')}
def completeness(s):
    x=s['normalized_complaint']; missing=[f for f in ['customer_name','product_name','batch_number','description'] if not x.get(f)]; status='COMPLETE' if not missing else ('PARTIALLY_COMPLETE' if len(missing)<3 else 'INCOMPLETE'); return {'missing_fields':missing,'completeness_assessment':{'status':status,'missing_fields':missing,'questions_to_ask':[f'Please provide {m.replace("_"," ")}.' for m in missing],'confidence':round(1-len(missing)/4,2)},**_stage(s,'Completeness checked')}
def risk(s):
    text=(s['raw_input']+' '+str(s['normalized_complaint'].get('description',''))).lower(); critical=any(x in text for x in ['contamination','adverse event','patient injury','foreign particle','sterility']); high=critical or s['normalized_complaint'].get('safety_concern')
    level='CRITICAL' if critical else ('HIGH' if high else ('MEDIUM' if any(x in text for x in ['broken','damaged','defect','discolor','crushed','tube removed','tubes removed']) else 'LOW')); sev='Critical' if level=='CRITICAL' else ('Major' if level in ['HIGH','MEDIUM'] else 'Minor'); priority='Urgent' if level=='CRITICAL' else ('High' if level=='HIGH' else ('Medium' if level=='MEDIUM' else 'Low'))
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
