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
        builder.add_node(
            "search_purchase_orders",
            self._nodes.search_purchase_orders,
        )
        builder.add_node(
            "search_service_tickets",
            self._nodes.search_service_tickets,
        )
        builder.add_node(
            "search_documents",
            self._nodes.search_documents,
        )

        builder.add_edge(START, "understand")
        builder.add_edge("understand", "find_supplier")
        builder.add_edge("find_supplier", "search_purchase_orders")
        builder.add_edge("search_purchase_orders", "search_service_tickets")
        builder.add_edge("search_service_tickets", "search_documents")
        builder.add_edge("search_documents", END)

        return builder.compile()

    def invoke(self, state: InvestigationState) -> InvestigationState:
        return cast(InvestigationState, self._graph.invoke(state))
