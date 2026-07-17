from typing import TypedDict, Optional

class ClusterBState(TypedDict):
    request_id:str
    patient_ref:str
    procedure_requested:str
    diagnosis_code:str
    urgency:str
    eligibility:dict
    policy_match:Optional[dict]
    documentation_status:Optional[dict]
    coding_valid:Optional[bool]
    coding_notes:Optional[str]
    errors:list[str]