from app.graph.state import AgentStepResult
from app.graph.state import WorkflowState


async def event_analysis_agent_node(state: WorkflowState) -> WorkflowState:
    tool_completed = state.get("event_analysis_tool_completed", False)
    result: AgentStepResult = {
        "agent_name": "Event Analysis Agent",
        "status": "stubbed",
        "summary": (
            "Event analysis agent received the alert from the supervisor."
            if not tool_completed
            else "Event analysis agent received the analysis result from the tool."
        ),
        "details": {
            "tool_completed": tool_completed,
            "next_real_capabilities": [
                "alert parsing",
                "pattern classification",
                "result summarization",
            ],
        },
    }
    return {
        "agent_results": [*state.get("agent_results", []), result],
        "current_stage": "event_analysis" if not tool_completed else "event_analysis_review",
        "category": "pending_event_analysis",
        "evidence": [
            *state.get("evidence", []),
            "Event Analysis Agent stub executed.",
        ],
    }
