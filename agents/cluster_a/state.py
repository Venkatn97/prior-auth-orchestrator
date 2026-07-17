from typing import TypedDict, Optional

class ClusterAState(TypedDict):
    request_id:str
    raw_request:str
    patient_ref:Optional[str]
    procedure_requested:Optional[str]
    diagnosis_code:Optional[str]
    eligibility:Optional[dict]
    urgency:Optional[str]
    errors:list[str]