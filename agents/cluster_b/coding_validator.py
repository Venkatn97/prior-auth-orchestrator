import json
import re
import boto3
from shared.config import settings
from shared.logging import get_logger
from shared.persistence import log_agent_decision
from agents.cluster_b.state import ClusterBState
from shared.bedrock_client import invoke_claude

logger = get_logger("coding_validator")
bedrock_runtime = boto3.client("bedrock-runtime", region_name=settings.aws_region)

ICD10_PATTERN = re.compile(r'^[A-TV-Z][0-9][0-9AB](\.[0-9A-TV-Z]{1,4})?$')


def coding_validator_node(state: ClusterBState) -> ClusterBState:
    logger.info("coding_validator_start", request_id=state["request_id"])

    diagnosis_code = state.get("diagnosis_code", "")

    format_valid = bool(ICD10_PATTERN.match(diagnosis_code.strip())) if diagnosis_code else False

    if not format_valid:
        state["coding_valid"] = False
        state["coding_notes"] = f"'{diagnosis_code}' does not match valid ICD-10 format"
        logger.info("coding_validator_format_invalid", request_id=state["request_id"], diagnosis_code=diagnosis_code)
        log_agent_decision(
            request_id=state["request_id"],
            cluster="cluster_b",
            agent_name="coding_validator",
            decision={"coding_valid": False, "coding_notes": state["coding_notes"]},
        )
        return state

    prompt = (
        "Is the following diagnosis code clinically consistent with the requested "
        "procedure? Return ONLY a JSON object with keys: consistent (true/false), "
        "notes (a short explanation).\n\n"
        f"Diagnosis code: {diagnosis_code}\n"
        f"Procedure requested: {state['procedure_requested']}"
    )



    try:

   
        raw_text =invoke_claude(prompt,max_tokens=150)
        parsed = json.loads(raw_text)

        state["coding_valid"] = parsed.get("consistent", False)
        state["coding_notes"] = parsed.get("notes", "")

        logger.info("coding_validator_success", request_id=state["request_id"], valid=state["coding_valid"])

    except Exception as e:
        logger.info("coding_validator_error", request_id=state["request_id"], error=str(e))
        state["errors"].append(f"coding_validator: {str(e)}")
        state["coding_valid"] = False
        state["coding_notes"] = "validation failed due to error"

    log_agent_decision(
        request_id=state["request_id"],
        cluster="cluster_b",
        agent_name="coding_validator",
        decision={"coding_valid": state["coding_valid"], "coding_notes": state["coding_notes"]},
    )

    return state