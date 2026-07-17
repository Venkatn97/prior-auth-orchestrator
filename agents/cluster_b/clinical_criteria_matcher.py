import json
import boto3
from shared.config import settings
from shared.logging import get_logger
from shared.persistence import log_agent_decision
from shared.vector_store import search_policies
from agents.cluster_b.state import ClusterBState
from shared.bedrock_client import invoke_claude

logger = get_logger("clinical_criteria_matcher")


def clinical_criteria_matcher_node(state: ClusterBState) -> ClusterBState:
    logger.info("clinical_criteria_matcher_start", request_id=state["request_id"])

    query = f"prior authorization requirements for {state['procedure_requested']} for diagnosis {state['diagnosis_code']}"
    cache_key=f"policy_search;{state['procedure_requested']}:{state['diagnosis_code']}"

    try:
        matches = search_policies(query, top_k=3)

        if not matches:
            state["policy_match"] = {"found": False, "requires_prior_auth": None}
            logger.info("no_policy_found", request_id=state["request_id"])
            log_agent_decision(
                request_id=state["request_id"],
                cluster="cluster_b",
                agent_name="clinical_criteria_matcher",
                decision=state["policy_match"],
            )
            return state

        policy_context = "\n\n".join([m["policy_text"] for m in matches])

        prompt = (
            "Based ONLY on the following policy text, determine if prior authorization "
            "is required for this request, and what criteria must be met. "
            "Return ONLY a JSON object with keys: requires_prior_auth (true/false), "
            "criteria (a short string describing what's required), "
            "confidence (high/medium/low based on how directly the policy addresses this case).\n\n"
            f"Policy text:\n{policy_context}\n\n"
            f"Procedure requested: {state['procedure_requested']}\n"
            f"Diagnosis code: {state['diagnosis_code']}"
        )




        raw_text = invoke_claude(prompt,max_tokens=300)
        parsed = json.loads(raw_text)

        state["policy_match"] = {
            "found": True,
            "requires_prior_auth": parsed.get("requires_prior_auth"),
            "criteria": parsed.get("criteria"),
            "confidence": parsed.get("confidence"),
            "source_matches": [{"score": m["score"], "text": m["policy_text"][:150]} for m in matches],
        }

        logger.info("clinical_criteria_matcher_success", request_id=state["request_id"], result=state["policy_match"])

    except Exception as e:
        logger.info("clinical_criteria_matcher_error", request_id=state["request_id"], error=str(e))
        state["errors"].append(f"clinical_criteria_matcher: {str(e)}")
        state["policy_match"] = {"found": False, "requires_prior_auth": None}

    log_agent_decision(
        request_id=state["request_id"],
        cluster="cluster_b",
        agent_name="clinical_criteria_matcher",
        decision=state["policy_match"],
    )

    return state