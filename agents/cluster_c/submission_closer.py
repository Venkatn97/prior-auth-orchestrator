from shared.logging import get_logger
from shared.persistence import log_agent_decision, update_request_status
from shared.models import RequestStatus
from agents.cluster_c.state import ClusterCState

logger = get_logger("submission_closer")


def submission_closer_node(state: ClusterCState) -> ClusterCState:
    logger.info("submission_closer_start", request_id=state["request_id"])

    decision = state.get("approval_decision")

    if decision in ("auto_approved", "approved"):
        state["final_status"] = "approved"
        update_request_status(state["request_id"], RequestStatus.approved)
    elif decision == "rejected":
        state["final_status"] = "denied"
        update_request_status(state["request_id"], RequestStatus.denied)
    else:
        state["final_status"] = "error"
        state["errors"].append("submission_closer: no valid approval decision found")

    logger.info("submission_closer_result", request_id=state["request_id"], final_status=state["final_status"])

    log_agent_decision(
        request_id=state["request_id"],
        cluster="cluster_c",
        agent_name="submission_closer",
        decision={"final_status": state["final_status"]},
    )

    if state["final_status"] in ("approved", "denied"):
        update_request_status(state["request_id"], RequestStatus.closed)

    return state