from langgraph.graph import StateGraph, END
from agents.cluster_a.state import ClusterAState
from agents.cluster_a.intake_parser import intake_parser_node
from agents.cluster_a.eligibility_checker import eligibility_checker_node
from agents.cluster_a.urgency_classifier import urgency_classifier_node

def build_cluster_a_graph():
    graph=StateGraph(ClusterAState)

    graph.add_node("intake_parser",intake_parser_node)
    graph.add_node("eligibility_checker",eligibility_checker_node)
    graph.add_node("urgency_classifier",urgency_classifier_node)

    graph.set_entry_point("intake_parser")
    graph.add_edge("intake_parser","eligibility_checker")
    graph.add_edge("eligibility_checker","urgency_classifier")
    graph.add_edge("urgency_classifier",END)

    return graph.compile()
