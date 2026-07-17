import time
import uuid
from agents.cluster_b.clinical_criteria_matcher import clinical_criteria_matcher_node
from shared.persistence import create_request

request_id = str(uuid.uuid4())
create_request(request_id=request_id, patient_ref="patient_001", raw_payload={"procedure": "MRI"})

state = {
    'request_id': request_id,
    'patient_ref': 'patient_001',
    'procedure_requested': 'MRI',
    'diagnosis_code': 'M54.5',
    'urgency': 'routine',
    'eligibility': {'found': True, 'eligible': True},
    'policy_match': None,
    'documentation_status': None,
    'coding_valid': None,
    'coding_notes': None,
    'errors': [],
}

start = time.time()
result1 = clinical_criteria_matcher_node(dict(state))
print("First call took:", round(time.time() - start, 2), "seconds")

start = time.time()
result2 = clinical_criteria_matcher_node(dict(state))
print("Second call took:", round(time.time() - start, 2), "seconds")
