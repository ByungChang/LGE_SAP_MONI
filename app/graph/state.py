from typing import Any
from typing import Literal
from typing import TypedDict

from app.models.alerts import AlertPayload


IncidentStatus = Literal["confirmed", "suspected", "insufficient_evidence"]


class AgentStepResult(TypedDict, total=False):
    agent_name: str
    status: str
    summary: str
    details: dict[str, Any]


class WorkflowState(TypedDict, total=False):
    alert: AlertPayload
    workflow_name: str
    supervisor_status: str
    current_stage: str
    guide_review_count: int
    max_guide_review_count: int
    event_analysis_tool_completed: bool
    sap_status_tool_completed: bool
    guide_generation_tool_completed: bool
    guide_quality_approved: bool
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
    escalation: dict[str, Any]
    operator_summary: str
    route_plan: list[str]
    agent_results: list[AgentStepResult]
    event_analysis_tool_context: dict[str, Any]
    sap_runtime_context: dict[str, Any]
    guide_generation_tool_context: dict[str, Any]
