from typing import TypedDict, Optional


class ClusterCState(TypedDict):
    request_id: str
    patient_ref: str
    procedure_requested: str
    diagnosis_code: str
    urgency: str
    eligibility: dict
    policy_match: dict
    documentation_status: dict
    coding_valid: bool
    coding_notes: str
    draft_summary: Optional[str]
    compliance_passed: Optional[bool]
    compliance_notes: Optional[str]
    requires_human_approval: Optional[bool]
    approval_decision: Optional[str]
    final_status: Optional[str]
    errors: list[str]