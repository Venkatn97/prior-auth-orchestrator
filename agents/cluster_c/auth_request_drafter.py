import json
import boto3
from shared.config import settings
from shared.logging import get_logger
from shared.persistence import log_agent_decision
from agents.cluster_c.state import ClusterCState
from shared.bedrock_client import invoke_claude

logger = get_logger("auth_request_drafter")



def auth_request_drafter_node(state: ClusterCState) -> ClusterCState:
    logger.info("auth_request_drafter_start", request_id=state["request_id"])

    prompt = (
        "Write a concise 3-4 sentence summary of this prior authorization case "
        "for a human reviewer. Include the procedure, diagnosis, eligibility status, "
        "urgency, whether policy criteria are met, and documentation completeness. "
        "Return ONLY the summary text, no JSON, no preamble.\n\n"
        f"Procedure: {state['procedure_requested']}\n"
        f"Diagnosis: {state['diagnosis_code']}\n"
        f"Eligibility: {state['eligibility']}\n"
        f"Urgency: {state['urgency']}\n"
        f"Policy match: {state['policy_match']}\n"
        f"Documentation status: {state['documentation_status']}\n"
        f"Coding valid: {state['coding_valid']} ({state['coding_notes']})"
    )

    try:
        summary=invoke_claude(prompt, max_tokens=300)
        state["draft_summary"] = summary
        logger.info("auth_request_drafter_success", request_id=state["request_id"])

    except Exception as e:
        logger.info("auth_request_drafter_error", request_id=state["request_id"], error=str(e))
        state["errors"].append(f"auth_request_drafter: {str(e)}")
        state["draft_summary"] = "Draft generation failed"

    log_agent_decision(
        request_id=state["request_id"],
        cluster="cluster_c",
        agent_name="auth_request_drafter",
        decision={"draft_summary": state["draft_summary"]},
    )

    return state