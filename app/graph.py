from langgraph.graph import StateGraph
from app.state import FinanceState
from app.agents.context_agent import context_agent
from app.agents.planner_agent import planner_agent
from app.agents.executor_agent import executor_agent
from app.agents.finalizer_agent import finalizer_agent
from app.memory.memory_manager import memory_manager
def _route_after_planner(state: FinanceState) -> str:
    action = state.get("next_action", "qa")
    if action == "final":
        return "finalizer"
    return "executor"
def _route_after_executor(state: FinanceState) -> str:
    if state.get("done"):
        return "finalizer"
    if state.get("step", 0) >= state.get("max_steps", 3):
        return "finalizer"
    return "planner"
def build_graph():
    graph = StateGraph(FinanceState)
    graph.add_node("context", context_agent)
    graph.add_node("planner", planner_agent)
    graph.add_node("executor", executor_agent)
    graph.add_node("finalizer", finalizer_agent)
    graph.add_node("memory", memory_manager)
    graph.set_entry_point("context")
    graph.add_edge("context", "planner")
    graph.add_conditional_edges(
        "planner",
        _route_after_planner,
        {
            "executor": "executor",
            "finalizer": "finalizer",
        },
    )

    graph.add_conditional_edges(
        "executor",
        _route_after_executor,
        {
            "planner": "planner",
            "finalizer": "finalizer",
        },
    )
    graph.add_edge("finalizer", "memory")
    graph.set_finish_point("memory")
    return graph.compile()