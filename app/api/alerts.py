from fastapi import APIRouter

from app.graph.supervisor import run_supervisor
from app.models.alerts import AlertPayload
from app.models.alerts import SupervisorResponse

router = APIRouter(tags=["alerts"])


@router.post("/alerts", response_model=SupervisorResponse)
async def handle_alert(payload: AlertPayload) -> SupervisorResponse:
    return await run_supervisor(payload)
