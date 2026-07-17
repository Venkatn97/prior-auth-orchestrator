import uuid
import pytest
from agents.cluster_a.graph import build_cluster_a_graph
from shared.persistence import create_request

graph = build_cluster_a_graph()


def run_cluster_a(raw_request: str, patient_hint: str):
    request_id = str(uuid.uuid4())
    create_request(request_id=request_id, patient_ref=patient_hint, raw_payload={"raw_request": raw_request})
    state = {
        'request_id': request_id,
        'raw_request': raw_request,
        'patient_ref': None,
        'procedure_requested': None,
        'diagnosis_code': None,
        'eligibility': None,
        'urgency': None,
        'errors': [],
    }
    return graph.invoke(state)


def test_extracts_correct_patient_ref():
    result = run_cluster_a(
        "Patient patient_001 needs an MRI for lower back pain, diagnosis code M54.5",
        "patient_001",
    )
    assert result["patient_ref"] == "patient_001"


def test_extracts_correct_procedure():
    result = run_cluster_a(
        "Patient patient_001 needs an MRI for lower back pain, diagnosis code M54.5",
        "patient_001",
    )
    assert result["procedure_requested"] == "MRI"


def test_eligible_patient_returns_eligible_true():
    result = run_cluster_a(
        "Patient patient_001 needs an MRI for lower back pain, diagnosis code M54.5",
        "patient_001",
    )
    assert result["eligibility"]["eligible"] is True
    assert result["eligibility"]["plan"] == "PPO Gold"


def test_ineligible_patient_returns_eligible_false():
    result = run_cluster_a(
        "Patient patient_002 needs an MRI for lower back pain, diagnosis code M54.5",
        "patient_002",
    )
    assert result["eligibility"]["eligible"] is False
    assert result["eligibility"]["plan"] == "HMO Basic"


def test_no_errors_on_valid_request():
    result = run_cluster_a(
        "Patient patient_001 needs an MRI for lower back pain, diagnosis code M54.5",
        "patient_001",
    )
    assert result["errors"] == []


def test_urgency_is_valid_value():
    result = run_cluster_a(
        "Patient patient_001 needs an MRI for lower back pain, diagnosis code M54.5",
        "patient_001",
    )
    assert result["urgency"] in ("routine", "urgent")