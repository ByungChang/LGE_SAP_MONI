from langgraph.graph import END
from langgraph.graph import StateGraph

from app.graph.nodes.event_analysis import event_analysis_agent_node
from app.graph.nodes.guide import guide_generation_agent_node
from app.graph.nodes.sap_status import sap_status_check_agent_node
from app.graph.nodes.supervisor import supervisor_agent_node
from app.graph.nodes.tools import event_analysis_tool_node
from app.graph.nodes.tools import guide_generation_tool_node
from app.graph.nodes.tools import sap_status_check_tool_node
from app.graph.state import WorkflowState
from app.models.alerts import AlertPayload
from app.models.alerts import Escalation
from app.models.alerts import SupervisorResponse


def route_after_event_analysis(state: WorkflowState) -> str:
    if not state.get("event_analysis_tool_completed", False):
        return "event_analysis_tool"
    return "supervisor_agent"


def route_after_supervisor_review(state: WorkflowState) -> str:
    current_stage = state.get("current_stage", "event_analysis")
    guide_review_count = state.get("guide_review_count", 0)
    max_review_count = state.get("max_guide_review_count", 3)

    if current_stage == "sap_status":
        return "sap_status_agent"
    if current_stage == "guide_generation":
        return "guide_generation_agent"
    if current_stage == "guide_quality_review":
        if guide_review_count >= max_review_count or state.get(
            "guide_quality_approved",
            False,
        ):
            return END
        return "guide_generation_agent"
    if current_stage == "completed":
        return END
    return "event_analysis_agent"


def route_after_sap_status_check(state: WorkflowState) -> str:
    if not state.get("sap_status_tool_completed", False):
        return "sap_status_tool"
    return "supervisor_agent"


def route_after_guide_generation(state: WorkflowState) -> str:
    if not state.get("guide_generation_tool_completed", False):
        return "guide_generation_tool"
    return "supervisor_agent"


def build_supervisor_workflow():
    workflow = StateGraph(WorkflowState)
    workflow.add_node("supervisor_agent", supervisor_agent_node)
    workflow.add_node("event_analysis_agent", event_analysis_agent_node)
    workflow.add_node("event_analysis_tool", event_analysis_tool_node)
    workflow.add_node("sap_status_agent", sap_status_check_agent_node)
    workflow.add_node("sap_status_tool", sap_status_check_tool_node)
    workflow.add_node("guide_generation_agent", guide_generation_agent_node)
    workflow.add_node("guide_generation_tool", guide_generation_tool_node)

    workflow.set_entry_point("supervisor_agent")
    workflow.add_conditional_edges(
        "supervisor_agent",
        route_after_supervisor_review,
        {
            "event_analysis_agent": "event_analysis_agent",
            "sap_status_agent": "sap_status_agent",
            "guide_generation_agent": "guide_generation_agent",
            END: END,
        },
    )

    workflow.add_conditional_edges(
        "event_analysis_agent",
        route_after_event_analysis,
        {
            "event_analysis_tool": "event_analysis_tool",
            "supervisor_agent": "supervisor_agent",
        },
    )
    workflow.add_edge("event_analysis_tool", "event_analysis_agent")

    workflow.add_conditional_edges(
        "sap_status_agent",
        route_after_sap_status_check,
        {
            "sap_status_tool": "sap_status_tool",
            "supervisor_agent": "supervisor_agent",
        },
    )
    workflow.add_edge("sap_status_tool", "sap_status_agent")

    workflow.add_conditional_edges(
        "guide_generation_agent",
        route_after_guide_generation,
        {
            "guide_generation_tool": "guide_generation_tool",
            "supervisor_agent": "supervisor_agent",
        },
    )
    workflow.add_edge("guide_generation_tool", "guide_generation_agent")
    return workflow.compile()


graph = build_supervisor_workflow()


async def run_supervisor(payload: AlertPayload) -> SupervisorResponse:
    final_state = await graph.ainvoke({"alert": payload})
    escalation = final_state.get(
        "escalation",
        {"required": False, "target": "", "reason": ""},
    )

    return SupervisorResponse(
        alert_id=payload.alert_id,
        category=final_state.get("category", "unclassified"),
        status=final_state.get("status", "insufficient_evidence"),
        business_impact=final_state.get("business_impact", "Not evaluated yet."),
        severity_assessment=final_state.get("severity_assessment", payload.severity),
        suspected_root_cause=final_state.get(
            "suspected_root_cause",
            "Not analyzed yet.",
        ),
        confidence=final_state.get("confidence", 0.0),
        evidence=final_state.get("evidence", []),
        missing_information=final_state.get("missing_information", []),
        recommended_actions=final_state.get("recommended_actions", []),
        sap_tcodes=final_state.get("sap_tcodes", []),
        escalation=Escalation(**escalation),
        operator_summary=final_state.get(
            "operator_summary",
            "Supervisor workflow finished without generating a live operator summary.",
        ),
    )
