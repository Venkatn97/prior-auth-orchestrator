import uuid
from langgraph.types import Command
from agents.cluster_c.graph import build_cluster_c_graph
from shared.persistence import create_request

graph = build_cluster_c_graph()


def build_state(request_id, documentation_complete, urgency="routine"):
    return {
        'request_id': request_id,
        'patient_ref': 'patient_001',
        'procedure_requested': 'MRI',
        'diagnosis_code': 'M54.5',
        'urgency': urgency,
        'eligibility': {'found': True, 'eligible': True, 'plan': 'PPO Gold', 'coverage_percent': 80},
        'policy_match': {'found': True, 'requires_prior_auth': True, 'criteria': 'conservative treatment required', 'confidence': 'high'},
        'documentation_status': {
            'overall_status': 'complete' if documentation_complete else 'incomplete',
            'required_documents': [],
        },
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


def test_complete_documentation_auto_approves():
    request_id = str(uuid.uuid4())
    create_request(request_id=request_id, patient_ref="patient_001", raw_payload={})
    state = build_state(request_id, documentation_complete=True)
    config = {"configurable": {"thread_id": request_id}}
    result = graph.invoke(state, config=config)
    assert result["approval_decision"] == "auto_approved"
    assert result["final_status"] == "approved"


def test_incomplete_documentation_requires_human_approval():
    request_id = str(uuid.uuid4())
    create_request(request_id=request_id, patient_ref="patient_001", raw_payload={})
    state = build_state(request_id, documentation_complete=False)
    config = {"configurable": {"thread_id": request_id}}
    result = graph.invoke(state, config=config)
    assert result.get("final_status") is None
    assert result.get("compliance_passed") is False


def test_human_can_approve_after_pause():
    request_id = str(uuid.uuid4())
    create_request(request_id=request_id, patient_ref="patient_001", raw_payload={})
    state = build_state(request_id, documentation_complete=False)
    config = {"configurable": {"thread_id": request_id}}
    graph.invoke(state, config=config)
    result = graph.invoke(Command(resume={"decision": "approved"}), config=config)
    assert result["approval_decision"] == "approved"
    assert result["final_status"] == "approved"


def test_human_can_reject_after_pause():
    request_id = str(uuid.uuid4())
    create_request(request_id=request_id, patient_ref="patient_001", raw_payload={})
    state = build_state(request_id, documentation_complete=False)
    config = {"configurable": {"thread_id": request_id}}
    graph.invoke(state, config=config)
    result = graph.invoke(Command(resume={"decision": "rejected"}), config=config)
    assert result["approval_decision"] == "rejected"
    assert result["final_status"] == "denied"