import uuid
from agents.cluster_b.graph import build_cluster_b_graph
from shared.persistence import create_request

graph = build_cluster_b_graph()


def run_cluster_b(procedure: str, diagnosis: str, patient_ref: str = "patient_001"):
    request_id = str(uuid.uuid4())
    create_request(request_id=request_id, patient_ref=patient_ref, raw_payload={"procedure": procedure})
    state = {
        'request_id': request_id,
        'patient_ref': patient_ref,
        'procedure_requested': procedure,
        'diagnosis_code': diagnosis,
        'urgency': 'routine',
        'eligibility': {'found': True, 'eligible': True, 'plan': 'PPO Gold', 'coverage_percent': 80},
        'policy_match': None,
        'documentation_status': None,
        'coding_valid': None,
        'coding_notes': None,
        'errors': [],
    }
    return graph.invoke(state)


def test_mri_requires_prior_auth():
    result = run_cluster_b("MRI", "M54.5")
    assert result["policy_match"]["found"] is True
    assert result["policy_match"]["requires_prior_auth"] is True


def test_valid_icd10_code_passes_format_check():
    result = run_cluster_b("MRI", "M54.5")
    assert result["coding_valid"] is True


def test_invalid_icd10_format_fails():
    result = run_cluster_b("MRI", "NOTAVALIDCODE")
    assert result["coding_valid"] is False
    assert "does not match valid ICD-10 format" in result["coding_notes"]


def test_documentation_status_has_required_fields():
    result = run_cluster_b("MRI", "M54.5")
    assert "overall_status" in result["documentation_status"]
    assert result["documentation_status"]["overall_status"] in ("complete", "incomplete")


def test_no_errors_on_valid_case():
    result = run_cluster_b("MRI", "M54.5")
    assert result["errors"] == []