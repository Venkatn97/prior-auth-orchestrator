from langgraph.types import interrupt
from shared.logging import get_logger
from shared.persistence import log_agent_decision
from agents.cluster_c.state import ClusterCState

logger = get_logger("human_approver_gatekeeper")


def human_approver_gatekeeper_node(state: ClusterCState) -> ClusterCState:
    logger.info("human_approver_gatekeeper_start", request_id=state["request_id"])

    auto_approve_eligible = (
        state.get("compliance_passed") is True
        and state.get("urgency") == "routine"
    )

    if auto_approve_eligible:
        state["requires_human_approval"] = False
        state["approval_decision"] = "auto_approved"
        logger.info("auto_approved", request_id=state["request_id"])
    else:
        state["requires_human_approval"] = True

        decision = interrupt({
            "request_id": state["request_id"],
            "draft_summary": state.get("draft_summary"),
            "compliance_passed": state.get("compliance_passed"),
            "compliance_notes": state.get("compliance_notes"),
            "urgency": state.get("urgency"),
            "message": "Human review required. Approve or reject this prior authorization request.",
        })

        state["approval_decision"] = decision.get("decision", "rejected")
        logger.info("human_decision_received", request_id=state["request_id"], decision=state["approval_decision"])

    log_agent_decision(
        request_id=state["request_id"],
        cluster="cluster_c",
        agent_name="human_approver_gatekeeper",
        decision={
            "requires_human_approval": state["requires_human_approval"],
            "approval_decision": state["approval_decision"],
        },
    )

    return state