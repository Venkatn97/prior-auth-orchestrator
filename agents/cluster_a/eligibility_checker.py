from shared.logging import get_logger
from agents.cluster_a.state import ClusterAState
from mcp_server.server import check_eligibility 
from shared.persistence import log_agent_decision

logger=get_logger("eligibility_checker")

def eligibility_checker_node(state:ClusterAState)->ClusterAState:
    logger.info("eligibility_checker_start",request_id=state["request_id"])

    patient_ref=state.get("patient_ref")

    if not patient_ref:
        logger.info("eligibility_checker_skipped_no_patiient_ref",request_id=state["request_id"])
        state["errors"].append("eligibility_checker:no patient_ref available")
        return state
    
    try:
        result=check_eligibility(patient_ref)
        state["eligibility"]=result
        logger.info("eligibility_checker_success",request_id=state["request_id"],result=result)
    except Exception as e :
        logger.info("eligibility_checker_error",request_id=state["request_id"],error=str(e))
        state["errors"].append(f"eligibility_checker:{str(e)}")
    
    log_agent_decision(
        request_id=state["request_id"],
        cluster="cluster_a",
        agent_name="eligibility_checker",
        decision=state.get("eligibility") or {},
    )
    
    return state
