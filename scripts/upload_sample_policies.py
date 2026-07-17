from shared.vector_store import index_document

sample_document = """
MRI imaging for lower back pain requires prior authorization unless conservative 
treatment for at least 6 weeks has failed. This includes physical therapy or 
medication trials. Emergency room visits do not require prior authorization 
regardless of diagnosis. This applies to all emergency presentations including 
trauma. Specialty medications for autoimmune conditions require prior authorization 
with documented trial and failure of at least two standard first-line treatments. 
Prior authorization requests are typically reviewed within 3 to 5 business days 
for standard requests, or 24 hours for urgent requests marked as expedited.
"""

if __name__ == "__main__":
    count = index_document(
        doc_id="sample_policy_v1",
        full_text=sample_document,
        category="general",
    )
    print(f"Indexed {count} question-chunk pairs")