from pinecone import Pinecone
from shared.config import settings
from shared.chunking import semantic_chunk
from shared.hype import generate_hypothetical_questions

pc=Pinecone(api_key=settings.pinecone_api_key)
index=pc.Index(settings.pinecone_index_name)


def index_document(doc_id:str,full_text:str,category:str="general")->int:
    chunks=semantic_chunk(full_text,doc_id)
    records=[]

    for chunk in chunks:
        questions=generate_hypothetical_questions(chunk["text"])
        for i, question in  enumerate(questions):
            records.append({
                "_id":f"{chunk['id']}_q{i}",
                "text":question,
                "original_chunk":chunk["text"],
                "category": category,


            })
    index.upsert_records(namespace="policies",records=records)
    return len(records)

def search_policies(query:str,top_k:int=3)->list[dict]:
    results=index.search(
        namespace="policies",
        query={"inputs":{"text":query},"top_k":top_k},
        
    )
    return[
        {
            "id":hit.id,
            "matched_question": hit.fields["text"],
            "policy_text":hit.fields["original_chunk"],
            "score":hit.score,
        }
        for hit in results.result.hits
    ]