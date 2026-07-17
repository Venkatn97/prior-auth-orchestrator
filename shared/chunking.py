import re
import numpy as np
from pinecone import Pinecone
from shared.config import settings

pc=Pinecone(api_key=settings.pinecone_api_key)

EMBED_MODEL="multilingual-e5-large"
SIMILARITY_THRESHOLD=0.78

def split_sentences(text:str)->list[str]:
    sentences=re.split(r'(?<=[.!?])\s+',text.strip())
    return [s.strip() for s in sentences if s.strip()]

def embed_sentences(sentences:list[str])->list[list[float]]:
    response=pc.inference.embed(
        model=EMBED_MODEL,
        inputs=[{"text":s} for s in sentences],
        parameters={"input_type":"passage","truncate":"END"},

    )
    return [item["values"] for item in response.data]

def cosine_similarity(a:list[float],b:list[float])->float:
    a,b=np.array(a),np.array(b)
    return float(np.dot(a,b)/(np.linalg.norm(a)* np.linalg.norm(b)))

def semantic_chunk(text:str,doc_id:str)->list[dict]:
    sentences=split_sentences(text)
    if len(sentences)<=1:
        return [{"id": f"{doc_id}_chunk_0","text":text}]
    
    embeddings=embed_sentences(sentences)

    chunks=[]
    current_chunk=[sentences[0]]

    for i in range(1,len(sentences)):
        sim=cosine_similarity(embeddings[i-1],embeddings[i])
        if sim<SIMILARITY_THRESHOLD:
            chunks.append(" ".join(current_chunk))
            current_chunk=[sentences[i]]
        else:
            current_chunk.append(sentences[i])
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return[
        {"id":f"{doc_id}_chunk_{i}","text":chunk}
         for i,chunk in enumerate(chunks)
        
    ]
