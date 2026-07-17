from agents.orchestrator import run_full_pipeline, resume_pipeline

result = run_full_pipeline(
    raw_request="Patient patient_001 needs an MRI for lower back pain, diagnosis code M54.5",
    patient_ref_hint="patient_001",
)

print("PAUSED:", result["paused_for_approval"])
print("REQUEST ID:", result["request_id"])
print("FINAL STATUS:", result["cluster_c"].get("final_status"))

if result["paused_for_approval"]:
    print("\n=== RESUMING ===")
    resumed = resume_pipeline(result["request_id"], "approved")
    print(resumed["cluster_c"].get("final_status"))
