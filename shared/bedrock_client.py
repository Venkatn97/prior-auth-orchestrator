import json
import boto3
from shared.config import settings 

bedrock_runtime=boto3.client("bedrock-runtime",region_name=settings.aws_region)

def invoke_claude(prompt:str,max_tokens:int=300)->str:
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens":max_tokens,
        "messages":[{"role":"user","content":prompt}],


    })

    response=bedrock_runtime.invoke_model(
        modelId=settings.bedrock_model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
        guardrailIdentifier=settings.bedrock_guardrail_id,
        guardrailVersion=settings.bedrock_guardrail_version,

    )

    result=json.loads(response["body"].read())
    raw_text=result["content"][0]["text"].strip()

    if raw_text.startswith("```"):
        raw_text=raw_text.strip("`")
        raw_text=raw_text.replace("json","",1).strip()
    
    return raw_text