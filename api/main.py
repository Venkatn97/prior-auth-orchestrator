from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel
from shared.logging import configure_logging, get_logger
from agents.orchestrator import run_full_pipeline, resume_pipeline


configure_logging()
logger=get_logger("api")

app=FastAPI(title="Prior Authorization Orchestrator")


class SubmitRequestBody(BaseModel):
    raw_request:str
    patient_ref_hint:str | None=None


class DecisionBody(BaseModel):
    decision:str

@app.post("/requests")
def submit_request(body:SubmitRequestBody):
    logger.info("api_submit_request")
    try:
        result= run_full_pipeline(
            raw_request=body.raw_request,
            patient_ref_hint=body.patient_ref_hint,
        )
        return {
            "request_id": result["request_id"],
            "paused_for_approval":result["paused_for_approval"],
            "cluster_a":result["cluster_a"],
            "cluster_b":result["cluster_b"],
            "cluster_c":result["cluster_c"],
            

        }
    except Exception as e:
        logger.info("api_submit_error",error=str(e))
        raise HTTPException(status_code=500,detail=str(e))
    
@app.post("/requests/{request_id}/decisions")
def submit_decision(request_id:str, body:DecisionBody):
    logger.info("api_decision",request_id=request_id,decision=body.decision)
    if body.decision not in ("approved","rejected"):
        raise HTTPException(status_code=400,detail="decision must be 'approved' or 'rejected'")
    
    try:
        result=resume_pipeline(request_id=request_id,decision=body.decision)
        return{
            "reuqest_id":request_id,
            "cluster_c":result["cluster_c"],
            
        }
    except Exception as e:
        logger.info("api_decision_error",request_id=request_id,error=str(e))
        raise HTTPException(status_code=500,detail=str(e))

@app.get("/health")
def health_check():
    return {"status":"ok"}


