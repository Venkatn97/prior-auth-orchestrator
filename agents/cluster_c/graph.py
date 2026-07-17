from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agents.cluster_c.state import ClusterCState
from agents.cluster_c.auth_request_drafter import auth_request_drafter_node
from agents.cluster_c.compliance_checker import compliance_checker_node
from agents.cluster_c.human_approver_gatekeeper import human_approver_gatekeeper_node
from agents.cluster_c.submission_closer import submission_closer_node


def build_cluster_c_graph():
    graph = StateGraph(ClusterCState)

    graph.add_node("auth_request_drafter", auth_request_drafter_node)
    graph.add_node("compliance_checker", compliance_checker_node)
    graph.add_node("human_approver_gatekeeper", human_approver_gatekeeper_node)
    graph.add_node("submission_closer", submission_closer_node)

    graph.set_entry_point("auth_request_drafter")
    graph.add_edge("auth_request_drafter", "compliance_checker")
    graph.add_edge("compliance_checker", "human_approver_gatekeeper")
    graph.add_edge("human_approver_gatekeeper", "submission_closer")
    graph.add_edge("submission_closer", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)