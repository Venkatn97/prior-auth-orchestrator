import json
import boto3
from shared.config import settings
from shared.logging import get_logger
from shared.persistence import log_agent_decision
from agents.cluster_b.state import ClusterBState
from shared.bedrock_client import invoke_claude

logger = get_logger("documentation_gatherer")
bedrock_runtime = boto3.client("bedrock-runtime", region_name=settings.aws_region)


def documentation_gatherer_node(state: ClusterBState) -> ClusterBState:
    logger.info("documentation_gatherer_start", request_id=state["request_id"])

    policy_match = state.get("policy_match") or {}
    criteria = policy_match.get("criteria", "No specific criteria found")

    prompt = (
        "Given the prior authorization criteria below, list what clinical "
        "documentation would be required to support this request, and mark "
        "each item as 'likely_available' or 'needs_followup' based on typical "
        "availability at time of request. Return ONLY a JSON object with keys: "
        "required_documents (a list of objects, each with 'document' and 'status'), "
        "overall_status ('complete' or 'incomplete').\n\n"
        f"Criteria: {criteria}\n"
        f"Procedure: {state['procedure_requested']}\n"
        f"Diagnosis code: {state['diagnosis_code']}"
    )



    try:

        raw_text = invoke_claude(prompt,max_tokens=400)

        parsed = json.loads(raw_text)
        state["documentation_status"] = parsed

        logger.info("documentation_gatherer_success", request_id=state["request_id"], result=parsed)

    except Exception as e:
        logger.info("documentation_gatherer_error", request_id=state["request_id"], error=str(e))
        state["errors"].append(f"documentation_gatherer: {str(e)}")
        state["documentation_status"] = {"required_documents": [], "overall_status": "incomplete"}

    log_agent_decision(
        request_id=state["request_id"],
        cluster="cluster_b",
        agent_name="documentation_gatherer",
        decision=state["documentation_status"],
    )

    return state