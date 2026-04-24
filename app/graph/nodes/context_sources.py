from app.graph.state import AgentStepResult
from app.graph.state import WorkflowState


async def db_context_node(state: WorkflowState) -> WorkflowState:
    result: AgentStepResult = {
        "agent_name": "DB Context Node",
        "status": "stubbed",
        "summary": "RDB/Graph context placeholder executed.",
        "details": {"source_family": "rdb_graph"},
    }
    return {
        "agent_results": [*state.get("agent_results", []), result],
        "db_context": {
            "status": "stubbed",
            "records_loaded": 0,
        },
    }


async def vector_context_node(state: WorkflowState) -> WorkflowState:
    result: AgentStepResult = {
        "agent_name": "Vector Context Node",
        "status": "stubbed",
        "summary": "Vector DB retrieval placeholder executed.",
        "details": {"source_family": "vector_db"},
    }
    return {
        "agent_results": [*state.get("agent_results", []), result],
        "vector_context": {
            "status": "stubbed",
            "documents_loaded": 0,
        },
    }
