import asyncio
from schemas.request_models import MaintenanceRequest
from services.workflow_runner import run_analysis

req = MaintenanceRequest(crack_type="Deep Foundation Settlement", severity="high", helmet_compliance=40.0, delay_risk="high")
try:
    print(run_analysis(req))
except Exception as e:
    import traceback
    traceback.print_exc()
