from typing import Any, cast
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from enterpriseops_ai.observability.context import agent_run_id_var
from enterpriseops_ai.orchestration.nodes import InvestigationNodes
from enterpriseops_ai.orchestration.state import InvestigationState


class InvestigationWorkflow:
    def __init__(self, nodes: InvestigationNodes) -> None:
        self._nodes = nodes
        self._graph = self._build_graph()

    def _build_graph(
        self,
    ) -> CompiledStateGraph[InvestigationState, None, Any, Any]:
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
        builder.add_node(
            "synthesize",
            self._nodes.synthesize,
        )

        builder.add_edge(START, "understand")
        builder.add_edge("understand", "find_supplier")
        builder.add_conditional_edges(
            "find_supplier",
            self._nodes.route_after_supplier,
            {
                "search_purchase_orders": "search_purchase_orders",
                "search_documents": "search_documents",
            },
        )
        builder.add_edge("search_purchase_orders", "search_service_tickets")
        builder.add_edge("search_service_tickets", "search_documents")
        builder.add_edge("search_documents", "synthesize")
        builder.add_edge("synthesize", END)

        return builder.compile()

    def invoke(self, state: InvestigationState) -> InvestigationState:
        agent_run_id = str(uuid4())
        token = agent_run_id_var.set(agent_run_id)
        try:
            return cast(InvestigationState, self._graph.invoke(state))
        finally:
            agent_run_id_var.reset(token)
