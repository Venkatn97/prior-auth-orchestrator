from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config= SettingsConfigDict(env_file=".env",env_file_encoding="utf-8")

    database_url:str
    redis_url:str
    aws_region:str
    bedrock_model_id:str
    log_level:str="INFO"
    environment:str="development"
    mcp_server_port:int=8001
    api_port:int=8000
    pinecone_api_key:str
    pinecone_index_name:str
    bedrock_guardrail_id:str
    bedrock_guardrail_version:str
    langsmith_api_key:str
    langsmith_project:str
    langsmith_tracing:bool=True
    langsmith_endpoint: str = "https://api.smith.langchain.com"

settings=Settings()