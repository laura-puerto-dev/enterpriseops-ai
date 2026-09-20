from typing import cast

from langgraph.graph import END, START, StateGraph

from enterpriseops_ai.orchestration.nodes import InvestigationNodes
from enterpriseops_ai.orchestration.state import InvestigationState


class InvestigationWorkflow:
    def __init__(self, nodes: InvestigationNodes) -> None:
        self._nodes = nodes
        self._graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(InvestigationState)

        builder.add_node("understand", self._nodes.understand)
        builder.add_node("find_supplier", self._nodes.find_supplier)

        builder.add_edge(START, "understand")
        builder.add_edge("understand", "find_supplier")
        builder.add_edge("find_supplier", END)

        return builder.compile()

    def invoke(self, state: InvestigationState) -> InvestigationState:
        return cast(InvestigationState, self._graph.invoke(state))
