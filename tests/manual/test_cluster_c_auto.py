import uuid
from agents.cluster_c.graph import build_cluster_c_graph
from shared.persistence import create_request

graph = build_cluster_c_graph()

request_id = str(uuid.uuid4())
create_request(request_id=request_id, patient_ref="patient_001", raw_payload={"procedure": "MRI"})

initial_state = {
    'request_id': request_id,
    'patient_ref': 'patient_001',
    'procedure_requested': 'MRI',
    'diagnosis_code': 'M54.5',
    'urgency': 'routine',
    'eligibility': {'found': True, 'eligible': True, 'plan': 'PPO Gold', 'coverage_percent': 80},
    'policy_match': {'found': True, 'requires_prior_auth': True, 'criteria': 'conservative treatment required', 'confidence': 'high'},
    'documentation_status': {'overall_status': 'complete', 'required_documents': []},
    'coding_valid': True,
    'coding_notes': 'Valid',
    'draft_summary': None,
    'compliance_passed': None,
    'compliance_notes': None,
    'requires_human_approval': None,
    'approval_decision': None,
    'final_status': None,
    'errors': [],
}

config = {"configurable": {"thread_id": request_id}}
final_state = graph.invoke(initial_state, config=config)
print(final_state)
