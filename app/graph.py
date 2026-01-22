from langgraph.graph import StateGraph
from app.state import FinanceState

from app.agents.router import router_agent
from app.agents.transaction_agent import transaction_agent
from app.agents.risk_agent import risk_agent
from app.agents.qa_agent import qa_agent
from app.memory.memory_manager import memory_manager

def build_graph():
    graph = StateGraph(FinanceState)

    graph.add_node("router", router_agent)
    graph.add_node("analysis", transaction_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("qa", qa_agent)
    graph.add_node("memory", memory_manager)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        lambda state: state["intent"],
        {
            "analysis": "analysis",
            "risk": "risk",
            "qa": "qa",
        }
    )

    graph.add_edge("analysis", "memory")
    graph.add_edge("risk", "memory")
    graph.add_edge("qa", "memory")

    graph.set_finish_point("memory")

    return graph.compile()
