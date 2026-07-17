import uuid
from shared.logging import get_logger
from shared.persistence import create_request
from agents.cluster_a.graph import build_cluster_a_graph
from agents.cluster_b.graph import build_cluster_b_graph
from agents.cluster_c.graph import build_cluster_c_graph
import os
from shared.config import settings

os.environ["LANGCHAIN_TRACING_V2"] = "true" if settings.langsmith_tracing else "false"
os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project

logger=get_logger("orchestrator")

cluster_a_graph=build_cluster_a_graph()
cluster_b_graph=build_cluster_b_graph()
cluster_c_graph=build_cluster_c_graph()

def run_full_pipeline(raw_request:str,patient_ref_hint:str=None)->dict:
    request_id=str(uuid.uuid4())
    logger.info("pipeline_state",request_id=request_id)

    create_request(
        request_id=request_id,
        patient_ref=patient_ref_hint or "unknown",
        raw_payload={"raw_request":raw_request},
    )

    a_state = {
        'request_id': request_id,
        'raw_request': raw_request,
        'patient_ref': None,
        'procedure_requested': None,
        'diagnosis_code': None,
        'eligibility': None,
        'urgency': None,
        'errors': [],
    }
    a_result=cluster_a_graph.invoke(a_state)
    logger.info("cluster_a_complete", request_id=request_id)

    b_state = {
        'request_id': request_id,
        'patient_ref': a_result['patient_ref'],
        'procedure_requested': a_result['procedure_requested'],
        'diagnosis_code': a_result['diagnosis_code'],
        'urgency': a_result['urgency'],
        'eligibility': a_result['eligibility'],
        'policy_match': None,
        'documentation_status': None,
        'coding_valid': None,
        'coding_notes': None,
        'errors': [],
    }
    b_result = cluster_b_graph.invoke(b_state)
    logger.info("cluster_b_complete", request_id=request_id)

    c_state = {
        'request_id': request_id,
        'patient_ref': b_result['patient_ref'],
        'procedure_requested': b_result['procedure_requested'],
        'diagnosis_code': b_result['diagnosis_code'],
        'urgency': b_result['urgency'],
        'eligibility': b_result['eligibility'],
        'policy_match': b_result['policy_match'],
        'documentation_status': b_result['documentation_status'],
        'coding_valid': b_result['coding_valid'],
        'coding_notes': b_result['coding_notes'],
        'draft_summary': None,
        'compliance_passed': None,
        'compliance_notes': None,
        'requires_human_approval': None,
        'approval_decision': None,
        'final_status': None,
        'errors': [],
    }

    config = {"configurable": {"thread_id": request_id}}
    c_result = cluster_c_graph.invoke(c_state, config=config)
    logger.info("cluster_c_complete", request_id=request_id, final_status=c_result.get('final_status'))

    return {
        "request_id": request_id,
        "cluster_a": a_result,
        "cluster_b": b_result,
        "cluster_c": c_result,
        "paused_for_approval": c_result.get("final_status") is None,
    }


def resume_pipeline(request_id: str, decision: str) -> dict:
    from langgraph.types import Command

    logger.info("pipeline_resume", request_id=request_id, decision=decision)
    config = {"configurable": {"thread_id": request_id}}
    result = cluster_c_graph.invoke(Command(resume={"decision": decision}), config=config)

    return {
        "request_id": request_id,
        "cluster_c": result,
    }




