from typing import Literal

from pydantic import BaseModel
from pydantic import Field


Severity = Literal["low", "medium", "high", "critical"]
IncidentStatus = Literal["confirmed", "suspected", "insufficient_evidence"]


class SystemContext(BaseModel):
    environment: str = Field(default="production")
    business_service: str | None = None
    criticality: str | None = None
    owner_team: str | None = None


class AlertPayload(BaseModel):
    alert_id: str
    title: str
    severity: Severity
    source: str
    sid: str
    client: str | None = None
    host: str | None = None
    timestamp: str
    raw_message: str
    system_context: SystemContext = Field(default_factory=SystemContext)


class Escalation(BaseModel):
    required: bool
    target: str
    reason: str


class SupervisorResponse(BaseModel):
    alert_id: str
    category: str
    status: IncidentStatus
    business_impact: str
    severity_assessment: str
    suspected_root_cause: str
    confidence: float
    evidence: list[str]
    missing_information: list[str]
    recommended_actions: list[str]
    sap_tcodes: list[str]
    escalation: Escalation
    operator_summary: str
