from langgraph.graph import StateGraph, END
from agents.cluster_b.state import ClusterBState
from agents.cluster_b.clinical_criteria_matcher import clinical_criteria_matcher_node
from agents.cluster_b.documentation_gatherer import documentation_gatherer_node
from agents.cluster_b.coding_validator import coding_validator_node

def build_cluster_b_graph():
    graph=StateGraph(ClusterBState)

    graph.add_node("clinical_criteria_matcher",clinical_criteria_matcher_node)
    graph.add_node("documentation_gatherer",documentation_gatherer_node)
    graph.add_node("coding_validator",coding_validator_node)

    graph.set_entry_point("clinical_criteria_matcher")
    graph.add_edge("clinical_criteria_matcher","documentation_gatherer")
    graph.add_edge("documentation_gatherer","coding_validator")
    graph.add_edge("coding_validator",END)


    return graph.compile()

