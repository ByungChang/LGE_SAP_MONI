from app.graph.state import AgentStepResult
from app.graph.state import WorkflowState


async def guide_generation_agent_node(state: WorkflowState) -> WorkflowState:
    tool_completed = state.get("guide_generation_tool_completed", False)
    result: AgentStepResult = {
        "agent_name": "Guide Generation Agent",
        "status": "stubbed",
        "summary": (
            "Guide generation agent received the validated context from the supervisor."
            if not tool_completed
            else "Guide generation agent received the generated guide from the tool."
        ),
        "details": {
            "tool_completed": tool_completed,
            "next_real_capabilities": [
                "operator guide drafting",
                "evidence-based response generation",
                "guide packaging",
            ],
        },
    }
    return {
        "agent_results": [*state.get("agent_results", []), result],
        "current_stage": "guide_generation" if not tool_completed else "guide_quality_review",
        "recommended_actions": [
            "No action generated yet. Replace guide generation agent stub with real remediation logic."
        ],
        "operator_summary": (
            "Guide generation agent placeholder executed. "
            "This workflow currently provides structure only."
        ),
    }
