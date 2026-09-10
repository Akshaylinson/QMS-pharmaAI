from app.ai.graph.workflow import complaint_graph
def test_intake_marks_damaged_packaging_medium():
    result=complaint_graph.invoke({'raw_input':'ABC Pharmaceuticals reports broken tablets and damaged blister packs for Batch PCM-2026-001.', 'source_type':'text','stages':[]})['final_response']
    assert result['risk']['risk_level']=='MEDIUM'
    assert result['completeness']['status'] in {'PARTIALLY_COMPLETE','INCOMPLETE'}
def test_intake_flags_safety_as_critical():
    result=complaint_graph.invoke({'raw_input':'A foreign particle caused a patient safety concern in Batch X-1.', 'source_type':'text','stages':[]})['final_response']
    assert result['risk']['risk_level']=='CRITICAL'
