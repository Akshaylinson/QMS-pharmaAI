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

def test_free_form_date_like_values_are_valid_create_payloads():
    complaint=ComplaintCreate(
        customer_name='name exactly as supplied',
        manufacturing_date='lot card says sometime around Q3 / unknown day',
        expiry_date='customer reports: not legible',
        complaint_date='Tuesday after delivery',
        received_date='entered by QA when received',
    )
    assert complaint.manufacturing_date=='lot card says sometime around Q3 / unknown day'
