import uuid
from agents.cluster_a.graph import build_cluster_a_graph
from shared.persistence import create_request

graph = build_cluster_a_graph()

request_id = str(uuid.uuid4())
raw_request = "Patient patient_002 needs an MRI for lower back pain, diagnosis code M54.5"

create_request(request_id=request_id, patient_ref="patient_002", raw_payload={"raw_request": raw_request})

initial_state = {
    'request_id': request_id,
    'raw_request': raw_request,
    'patient_ref': None,
    'procedure_requested': None,
    'diagnosis_code': None,
    'eligibility': None,
    'urgency': None,
    'errors': [],
}

final_state = graph.invoke(initial_state)
print(final_state)