from app.graph.state import AgentStepResult
from app.graph.state import WorkflowState


async def sap_status_check_agent_node(state: WorkflowState) -> WorkflowState:
    tool_completed = state.get("sap_status_tool_completed", False)
    result: AgentStepResult = {
        "agent_name": "SAP Status Check Agent",
        "status": "stubbed",
        "summary": (
            "SAP status check agent received the analysis context from the supervisor."
            if not tool_completed
            else "SAP status check agent received the runtime verification result from the tool."
        ),
        "details": {
            "tool_completed": tool_completed,
            "next_real_capabilities": [
                "MCP invocation",
                "runtime health verification",
                "status summarization",
            ],
        },
    }
    return {
        "agent_results": [*state.get("agent_results", []), result],
        "current_stage": "sap_status" if not tool_completed else "sap_status_review",
        "sap_runtime_context": {
            "status": "stubbed",
            "checked": tool_completed,
        },
        "evidence": [
            *state.get("evidence", []),
            "SAP Status Check Agent stub executed.",
        ],
        "sap_tcodes": [],
    }
