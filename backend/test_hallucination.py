import json
from dotenv import load_dotenv
load_dotenv()
from schemas.request_models import MaintenanceRequest
from services.workflow_runner import run_analysis

request = MaintenanceRequest(
    crack_type="Deep Foundation Settlement",
    severity="high",
    helmet_compliance=100.0,
    delay_risk="high"
)

result = run_analysis(request)

print("="*50)
print("AGENT 4: RETRIEVED RAG CONTEXT (TRUTH)")
print("="*50)
print(result['rag_context'])
print("\n" + "="*50)
print("AGENT 6: FINAL LLM RECOMMENDATION")
print("="*50)
print(result['recommendation'])
print("="*50)
