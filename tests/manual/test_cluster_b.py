import uuid
from agents.cluster_b.graph import build_cluster_b_graph
from shared.persistence import create_request

graph = build_cluster_b_graph()

request_id = str(uuid.uuid4())

create_request(
    request_id=request_id,
    patient_ref="patient_002",
    raw_payload={"procedure": "MRI", "diagnosis": "M54.5"},
)

initial_state = {
    'request_id': request_id,
    'patient_ref': 'patient_002',
    'procedure_requested': 'MRI',
    'diagnosis_code': 'M54.5',
    'urgency': 'routine',
    'eligibility': {'found': True, 'eligible': False, 'plan': 'HMO Basic', 'coverage_percent': 0},
    'policy_match': None,
    'documentation_status': None,
    'coding_valid': None,
    'coding_notes': None,
    'errors': [],
}

final_state = graph.invoke(initial_state)
print(final_state)
