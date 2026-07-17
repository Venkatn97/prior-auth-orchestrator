import json 
import boto3
from shared.config import settings
from shared.logging import get_logger
from agents.cluster_a.state import ClusterAState
from shared.persistence import log_agent_decision
from shared.bedrock_client import invoke_claude
logger=get_logger("urgency_classifier")

def urgency_classifier_node(state:ClusterAState)->ClusterAState:
    logger.info("urgency_classifier_start",request_id=state["request_id"])

    prompt=(
        "Classify the urgency of this prior authorization request as either"
        "'routine' or 'urgent'. Urgent means the delay could seriously harm "
        " the patient (e.g. cancer, stroke, servere trauma, acute conditions)." 
        "Return ONLY a JSON object with a single key 'urgency' set to either"
        "'routine' or 'urgent'.\n\n"
        f"Procdure: {state.get('procedure_requested')}\n"
        f"Diagnosis code:{state.get('diagonsis_code')}\n"
        f"Original request:{state['raw_request']}"
    )

    try:
        raw_text=invoke_claude(prompt,max_tokens=100)
        parsed=json.loads(raw_text)
        state["urgency"]=parsed.get("urgency","routine")

        logger.info("urgency_classifier_success",request_id=state["request_id"],urgency=state["urgency"])

    except Exception as e:
        logger.info("urgency_classifer_error",request_id=state["request_id"],error=str(e))
        state["errors"].append(f"urgency_classifier:{str(e)}")
        state["urgency"]="routine"
    
    log_agent_decision(
        request_id=state["request_id"],
        cluster="cluster_a",
        agent_name="urgency_classifier",
        decision={"urgency": state.get("urgency")},
    )
    
    return state




