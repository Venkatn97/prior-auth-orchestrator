import json
import boto3
from shared.config import settings
from shared.logging import get_logger
from agents.cluster_a.state import ClusterAState
from shared.persistence import log_agent_decision
from shared.bedrock_client import invoke_claude

logger=get_logger("intake_parser")


def intake_parser_node(state:ClusterAState)->ClusterAState:
    logger.info("intake_parser_start",request_id=state["request_id"])

    prompt=(
        "Extract the following fields from this prior authorization request."
        "Return ONLY a JSON object with keys: patient_ref, procedure_requested,"
        "diagnosis_code. Use null for any field not metioned.\n\n"
        f"Request:\n{state['raw_request']}"
    )



    try:
        raw_text=invoke_claude(prompt,max_tokens=200)
        parsed=json.loads(raw_text)

        state["patient_ref"]=parsed.get("patient_ref")
        state["procedure_requested"]=parsed.get("procedure_requested")
        state["diagnosis_code"]=parsed.get("diagnosis_code")

        logger.info("intake_parser_success",request_id=state["request_id"],parsed=parsed)
    
    except Exception as e :
        logger.info("intake_parser_error",request_id=state["request_id"],error=str(e))
        state["errors"].append(f"intake_parser:{str(e)}")
    
    log_agent_decision(
        request_id=state["request_id"],
        cluster="cluster_a",
        agent_name="intake_parser",
        decision={
            "patient_ref": state.get("patient_ref"),
            "procedure_requested": state.get("procedure_requested"),
            "diagnosis_code": state.get("diagnosis_code"),
        },
    )
    
    return state