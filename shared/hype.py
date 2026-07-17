import json
import boto3
from shared.config import settings

bedrock_runtime =boto3.client("bedrock-runtime",region_name=settings.aws_region)

def generate_hypothetical_questions(chunk_text:str, num_questions:int=3)->list[str]:
    prompt=(
        f"Given this policy text,generate {num_questions} realistic questions"
        f"that this text would answer. Return ONLY a json array of strings"
        f"nothing else.\n\n Policy text:\n{chunk_text}"
    )

    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens":300,
        "messages":[{"role":"user","content":prompt}],
    })

    response =bedrock_runtime.invoke_model(
        modelId=settings.bedrock_model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
    )

    result=json.loads(response["body"].read())
    raw_text=result["content"][0]["text"].strip()

    if raw_text.startswith("```"):
        raw_text=raw_text.strip("`")
        raw_text=raw_text.replace("json","",1).strip()

    try:
        questions=json.loads(raw_text)
    except json.JSONDecodeError:
        questions=[raw_text]
    
    return questions

