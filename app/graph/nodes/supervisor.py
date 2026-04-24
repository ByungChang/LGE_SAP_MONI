from app.graph.state import AgentStepResult
from app.graph.state import WorkflowState
from app.graph.utils import normalize_alert_payload


async def supervisor_agent_node(state: WorkflowState) -> WorkflowState:
    alert = normalize_alert_payload(state.get("alert"))
    current_stage = state.get("current_stage")

    if alert is None:
        result: AgentStepResult = {
            "agent_name": "Supervisor Agent",
            "status": "waiting_for_input",
            "summary": "Workflow started without an alert payload.",
            "details": {
                "required_input": "alert",
                "expected_fields": [
                    "alert_id",
                    "title",
                    "severity",
                    "source",
                    "sid",
                    "timestamp",
                    "raw_message",
                    "system_context",
                ],
            },
        }
        return {
            "workflow_name": "sap_monitoring_supervisor_workflow",
            "supervisor_status": "waiting_for_alert",
            "current_stage": "awaiting_input",
            "guide_review_count": 0,
            "max_guide_review_count": 3,
            "event_analysis_tool_completed": False,
            "sap_status_tool_completed": False,
            "guide_generation_tool_completed": False,
            "guide_quality_approved": False,
            "category": "input_missing",
            "status": "insufficient_evidence",
            "business_impact": "Cannot evaluate without alert input.",
            "severity_assessment": "unknown",
            "suspected_root_cause": "No alert payload was provided to the workflow.",
            "confidence": 0.0,
            "evidence": [],
            "missing_information": ["alert"],
            "recommended_actions": [
                "Provide an alert object in the LangGraph Studio input before running the workflow."
            ],
            "sap_tcodes": [],
            "escalation": {"required": False, "target": "", "reason": ""},
            "operator_summary": "Workflow is waiting for an alert payload.",
            "route_plan": [],
            "agent_results": [result],
        }

    if current_stage is None:
        result: AgentStepResult = {
            "agent_name": "Supervisor Agent",
            "status": "stubbed",
            "summary": "Supervisor agent received the alert and started orchestration.",
            "details": {
                "alert_id": alert.alert_id,
                "sid": alert.sid,
                "severity": alert.severity,
            },
        }
        return {
            "workflow_name": "sap_monitoring_supervisor_workflow",
            "supervisor_status": "initialized",
            "current_stage": "event_analysis",
            "guide_review_count": 0,
            "max_guide_review_count": 3,
            "event_analysis_tool_completed": False,
            "sap_status_tool_completed": False,
            "guide_generation_tool_completed": False,
            "guide_quality_approved": False,
            "category": "unclassified",
            "status": "insufficient_evidence",
            "business_impact": "Not evaluated yet.",
            "severity_assessment": alert.severity,
            "suspected_root_cause": "Not analyzed yet.",
            "confidence": 0.0,
            "evidence": [f"Alert received from source={alert.source}"],
            "missing_information": [
                "Event analysis result",
                "SAP runtime validation result",
                "Operator guide synthesis result",
            ],
            "recommended_actions": [],
            "sap_tcodes": [],
            "escalation": {"required": False, "target": "", "reason": ""},
            "operator_summary": "Supervisor workflow initialized. No operational action generated yet.",
            "route_plan": [
                "event_analysis_agent",
                "sap_status_agent",
                "guide_generation_agent",
            ],
            "agent_results": [result],
        }

    review_count = state.get("guide_review_count", 0)
    max_review_count = state.get("max_guide_review_count", 3)
    result = {
        "agent_name": "Supervisor Agent",
        "status": "stubbed",
        "summary": "Supervisor agent reviewed the latest agent output.",
        "details": {
            "current_stage": current_stage,
            "guide_review_count": review_count,
            "max_guide_review_count": max_review_count,
        },
    }

    updated_state: WorkflowState = {
        "agent_results": [*state.get("agent_results", []), result],
        "supervisor_status": "reviewing",
    }

    if current_stage == "event_analysis_review":
        updated_state["current_stage"] = "sap_status"
    elif current_stage == "sap_status_review":
        updated_state["current_stage"] = "guide_generation"
    elif current_stage == "guide_quality_review":
        next_review_count = review_count + 1
        updated_state["guide_review_count"] = next_review_count
        updated_state["guide_quality_approved"] = False
        if next_review_count >= max_review_count:
            updated_state["current_stage"] = "completed"
        else:
            updated_state["current_stage"] = "guide_generation"
            updated_state["guide_generation_tool_completed"] = False
        updated_state["operator_summary"] = (
            "Supervisor reviewed the generated guide placeholder. "
            "This review loop is still a stub."
        )

    return updated_state
