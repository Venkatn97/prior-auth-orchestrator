from fastmcp import FastMCP
from shared.logging import configure_logging, get_logger
from shared.vector_store import search_policies

configure_logging()
logger=get_logger("mcp_server")

mcp=FastMCP("prior-auth-tools")

FAKE_ELIGIBILITY_DB={
        "patient_001": {
        "eligible": True,
        "plan": "PPO Gold",
        "coverage_percent": 80,
    },
    "patient_002": {
        "eligible": False,
        "plan": "HMO Basic",
        "coverage_percent": 0,
    },
}

@mcp.tool()
def check_eligibility(patient_ref:str)->dict:
    logger.info("checming_eligibility",patient_ref=patient_ref)
    record= FAKE_ELIGIBILITY_DB.get(patient_ref)

    if record is None:
        logger.info("eligibility_not_found", patient_ref=patient_ref)
        return {"found":False,"eligible":False}
    
    logger.info("eligibility_found",patient_ref=patient_ref, eligible=record["eligible"])
    return {"found":True, **record}

@mcp.tool()
def search_policy(question:str)->dict:
    logger.info("searching_policy",question=question)

    results=search_policies(question,top_k=3)

    if not results:
        logger.info("no_policy_matches",question=question)
        return {"found":False,"matches":[]}
    
    logger.info("policy_matches_found",question=question, count=len(results))
    return {"found":True,"matches":results}
    



if __name__=="__main__":
    mcp.run
