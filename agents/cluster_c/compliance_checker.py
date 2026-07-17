from shared.logging import get_logger
from shared.persistence import log_agent_decision
from agents.cluster_c.state import ClusterCState

logger = get_logger("compliance_checker")


def compliance_checker_node(state: ClusterCState) -> ClusterCState:
    logger.info("compliance_checker_start", request_id=state["request_id"])

    issues = []

    if not state.get("coding_valid"):
        issues.append("diagnosis code failed clinical consistency check")

    documentation_status = state.get("documentation_status") or {}
    if documentation_status.get("overall_status") == "incomplete":
        issues.append("required documentation is incomplete")

    eligibility = state.get("eligibility") or {}
    if not eligibility.get("eligible"):
        issues.append("patient is not currently eligible under their plan")

    passed = len(issues) == 0

    state["compliance_passed"] = passed
    state["compliance_notes"] = "; ".join(issues) if issues else "No compliance issues found"

    logger.info("compliance_checker_result", request_id=state["request_id"], passed=passed, issues=issues)

    log_agent_decision(
        request_id=state["request_id"],
        cluster="cluster_c",
        agent_name="compliance_checker",
        decision={"compliance_passed": passed, "compliance_notes": state["compliance_notes"]},
    )

    return state