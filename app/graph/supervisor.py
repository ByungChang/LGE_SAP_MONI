from typing import TypedDict

from langgraph.graph import END
from langgraph.graph import StateGraph

from app.models.alerts import AlertPayload
from app.models.alerts import Escalation
from app.models.alerts import SupervisorResponse
from app.services.bedrock import BedrockService


class SupervisorState(TypedDict, total=False):
    alert: AlertPayload
    category: str
    status: str
    business_impact: str
    severity_assessment: str
    suspected_root_cause: str
    confidence: float
    evidence: list[str]
    missing_information: list[str]
    recommended_actions: list[str]
    sap_tcodes: list[str]
    escalation: dict
    operator_summary: str


async def analyze_event(state: SupervisorState) -> SupervisorState:
    alert = state["alert"]
    category = "performance" if "response time" in alert.raw_message.lower() else "general"

    return {
        "category": category,
        "status": "suspected",
        "business_impact": (
            f"{alert.system_context.business_service or 'core SAP service'} may be affected"
        ),
        "severity_assessment": alert.severity,
        "suspected_root_cause": "Initial symptom detected from monitoring alert",
        "confidence": 0.62,
        "evidence": [
            f"Alert source: {alert.source}",
            f"Alert severity: {alert.severity}",
            f"Original message: {alert.raw_message}",
        ],
        "missing_information": ["Current SAP runtime validation results"],
    }


async def validate_sap(state: SupervisorState) -> SupervisorState:
    alert = state["alert"]
    needs_escalation = alert.severity in {"high", "critical"}

    return {
        "status": "suspected",
        "confidence": 0.74 if needs_escalation else 0.68,
        "evidence": [
            *state["evidence"],
            "Runtime SAP validation is mocked in this initial scaffold",
        ],
        "recommended_actions": [
            "Check current SAP work process status",
            "Review recent logs and dumps before taking corrective action",
            "Validate whether business transactions are failing",
        ],
        "sap_tcodes": ["SM50", "ST03N"] if state["category"] == "performance" else ["SM21"],
        "escalation": {
            "required": needs_escalation,
            "target": "SAP Basis L2" if needs_escalation else "",
            "reason": "High-severity production alert requires human review"
            if needs_escalation
            else "",
        },
    }


async def build_operator_guide(state: SupervisorState) -> SupervisorState:
    bedrock = BedrockService()
    summary = await bedrock.summarize(
        f"Create a concise operator summary for alert {state['alert'].alert_id}"
    )

    return {
        "operator_summary": (
            f"{state['alert'].sid} alert categorized as {state['category']}. "
            f"Immediate action: {state['recommended_actions'][0]}. "
            f"{summary}"
        )
    }


def _build_graph():
    workflow = StateGraph(SupervisorState)
    workflow.add_node("analyze_event", analyze_event)
    workflow.add_node("validate_sap", validate_sap)
    workflow.add_node("build_operator_guide", build_operator_guide)
    workflow.set_entry_point("analyze_event")
    workflow.add_edge("analyze_event", "validate_sap")
    workflow.add_edge("validate_sap", "build_operator_guide")
    workflow.add_edge("build_operator_guide", END)
    return workflow.compile()


graph = _build_graph()


async def run_supervisor(payload: AlertPayload) -> SupervisorResponse:
    final_state = await graph.ainvoke({"alert": payload})
    escalation = final_state.get(
        "escalation",
        {"required": False, "target": "", "reason": ""},
    )

    return SupervisorResponse(
        alert_id=payload.alert_id,
        category=final_state["category"],
        status=final_state["status"],
        business_impact=final_state["business_impact"],
        severity_assessment=final_state["severity_assessment"],
        suspected_root_cause=final_state["suspected_root_cause"],
        confidence=final_state["confidence"],
        evidence=final_state["evidence"],
        missing_information=final_state["missing_information"],
        recommended_actions=final_state["recommended_actions"],
        sap_tcodes=final_state["sap_tcodes"],
        escalation=Escalation(**escalation),
        operator_summary=final_state["operator_summary"],
    )
