from langgraph.graph import StateGraph, START, END
from agents.state import AgentState
from agents.nodes.agent1_condition import assess_condition
from agents.nodes.agent2_risk import assess_risk
from agents.nodes.agent3_priority import assess_priority
from agents.nodes.agent4_planning import plan_maintenance
from agents.nodes.agent5_resources import optimize_resources
from agents.nodes.agent6_llm import generate_recommendation

import concurrent.futures

# Initialize the StateGraph with our Shared State schema
workflow = StateGraph(AgentState)

def parallel_assessments(state: AgentState) -> dict:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        f1 = executor.submit(assess_risk, state)
        f2 = executor.submit(assess_priority, state)
        f3 = executor.submit(plan_maintenance, state)
        f4 = executor.submit(optimize_resources, state)
        
        result = {}
        for f in [f1, f2, f3, f4]:
            result.update(f.result())
        return result

# Add nodes
workflow.add_node("Agent1_Condition", assess_condition)
workflow.add_node("Parallel_Assessments", parallel_assessments)
workflow.add_node("Agent6_LLM", generate_recommendation)

# Define the flow (Edges)
workflow.add_edge(START, "Agent1_Condition")
workflow.add_edge("Agent1_Condition", "Parallel_Assessments")
workflow.add_edge("Parallel_Assessments", "Agent6_LLM")
workflow.add_edge("Agent6_LLM", END)

# Compile the graph into a runnable application
app = workflow.compile()
