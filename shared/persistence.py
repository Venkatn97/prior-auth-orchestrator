from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.config import settings
from shared.models import Request, AgentDecision, RequestStatus

engine=create_engine(settings.database_url)
SessionLocal=sessionmaker(bind=engine)

def create_request(request_id:str, patient_ref:str, raw_payload:dict)->None:
    session=SessionLocal()
    try:
        existing =session.get(Request,request_id)
        if existing:
            return
        req=Request(
            id=request_id,
            patient_ref=patient_ref,
            status=RequestStatus.intake,
            payload=raw_payload

        )
        session.add(req)
        session.commit()
    
    finally:
        session.close()

def log_agent_decision(request_id:str, cluster:str,agent_name:str,decision:dict,reasoning:str=None)->None:
    session=SessionLocal()
    try:
        entry=AgentDecision(
            request_id=request_id,
            cluster=cluster,
            agent_name=agent_name,
            decision=decision,
            reasoning=reasoning,
        )
        session.add(entry)
        session.commit()
    finally:
        session.close()

def update_request_status(request_id:str,status:RequestStatus)->None:
    session=SessionLocal()
    try:
        req=session.get(Request,request_id)
        if req:
            req.status=status
            session.commit()
    finally:
        session.close()
    
    
