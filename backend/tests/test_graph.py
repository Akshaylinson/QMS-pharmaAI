from app.ai.graph.workflow import complaint_graph
from app.schemas.complaint import ComplaintCreate
def test_intake_marks_damaged_packaging_medium():
    result=complaint_graph.invoke({'raw_input':'ABC Pharmaceuticals reports broken tablets and damaged blister packs for Batch PCM-2026-001.', 'source_type':'text','stages':[]})['final_response']
    assert result['risk']['risk_level']=='MEDIUM'
    assert result['completeness']['status'] in {'PARTIALLY_COMPLETE','INCOMPLETE'}
def test_intake_flags_safety_as_critical():
    result=complaint_graph.invoke({'raw_input':'A foreign particle caused a patient safety concern in Batch X-1.', 'source_type':'text','stages':[]})['final_response']
    assert result['risk']['risk_level']=='CRITICAL'

def test_named_field_value_is_preserved_without_a_format_rule():
    value='MFG stamp unreadable — customer supplied 07?alpha / follow-up pending'
    result=complaint_graph.invoke({'raw_input':f'Change manufacturing date to {value}', 'source_type':'text','stages':[]})['final_response']
    assert result['extracted_complaint']['manufacturing_date']==value

def test_narrative_batch_reference_does_not_capture_the_rest_of_the_complaint():
    text=(
        'Apollo Pharmacy reported that 12 discolored capsules were found in a sealed bottle '
        'of Amoxicillin Capsules 500 mg. The complaint was received by email for batch '
        'AMX240602, manufactured in March 2026 and expiring in February 2028. '
        'The product originated from Block B, and the primary packaging material may be impacted. '
        'The customer is requesting an investigation and replacement.'
    )
    result=complaint_graph.invoke({'raw_input':text, 'source_type':'text','stages':[]})['final_response']
    extracted=result['extracted_complaint']
    assert extracted['batch_number']=='AMX240602'
    assert extracted['batch_number'] != text[text.index('AMX240602'):]
    assert extracted['description']==text

def test_unlabelled_narrative_fallback_extracts_evidence_based_complaint_fields():
    text=(
        'english medicals had a complaint regarding their recent purchase of asthalin inhalers '
        'that were produced in february 2026 which expires on march 2029. Upto 50 products '
        'were completely crushed or had their tubes removed, the batch number the customer mentioned was BCX500'
    )
    extracted=complaint_graph.invoke({'raw_input':text, 'source_type':'text','stages':[]})['final_response']['extracted_complaint']
    assert extracted['customer_name']=='english medicals'
    assert extracted['product_name'].lower()=='asthalin inhalers'
    assert extracted['batch_number']=='BCX500'
    assert extracted['affected_quantity'].lower()=='50 products'
    assert extracted['manufacturing_date'].lower()=='february 2026'
    assert extracted['expiry_date'].lower()=='march 2029'
    assert extracted['complaint_type']=='Packaging Damage'
    assert extracted['risk_level']=='MEDIUM'

def test_free_form_date_like_values_are_valid_create_payloads():
    complaint=ComplaintCreate(
        customer_name='name exactly as supplied',
        manufacturing_date='lot card says sometime around Q3 / unknown day',
        expiry_date='customer reports: not legible',
        complaint_date='Tuesday after delivery',
        received_date='entered by QA when received',
    )
    assert complaint.manufacturing_date=='lot card says sometime around Q3 / unknown day'
