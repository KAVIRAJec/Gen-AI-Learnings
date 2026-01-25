"""
LangGraph workflow for Multi-Agent Support System.
Implements the graph structure with Supervisor routing to specialist agents.
"""

import sys
import os

from langgraph.graph import StateGraph, END
from agents.supervisor import SupervisorAgent, AgentState
from agents.it_agent import ITAgent
from agents.finance_agent import FinanceAgent

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MultiAgentGraph:
    """
    Multi-agent graph that routes queries using LangGraph.
    
    The graph structure:
    1. START -> Supervisor (classification)
    2. Supervisor -> IT Agent (if IT query)
    3. Supervisor -> Finance Agent (if Finance query)
    4. Supervisor -> Clarification (if UNCLEAR)
    5. All paths -> END
    """
    
    def __init__(self):
        """Initialize the multi-agent graph with supervisor and workflow."""
        print("-> Initializing Multi-Agent Graph...")
        
        # Initialize agents
        self.supervisor = SupervisorAgent()
        self.it_agent = ITAgent()
        self.finance_agent = FinanceAgent()
        
        # Build the graph
        self.graph = self._build_graph()
        
        print("-> Multi-Agent Graph initialized successfully")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            StateGraph: Compiled graph ready for execution
        """
        # Create a new graph with AgentState
        workflow = StateGraph(AgentState)
        
        # Add supervisor node
        workflow.add_node("supervisor", self._supervisor_node)
        
        # Add placeholder nodes for specialist agents
        workflow.add_node("it_agent", self._it_agent_node)
        workflow.add_node("finance_agent", self._finance_agent_node)
        workflow.add_node("clarification", self._clarification_node)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional edges from supervisor to specialist agents
        workflow.add_conditional_edges(
            "supervisor",
            lambda state: state["route"],
            {
                "IT": "it_agent",
                "FINANCE": "finance_agent",
                "UNCLEAR": "clarification"
            }
        )
        
        workflow.add_edge("it_agent", END)
        workflow.add_edge("finance_agent", END)
        workflow.add_edge("clarification", END)
        
        # Compile the graph
        return workflow.compile()
    
    def _supervisor_node(self, state: AgentState) -> AgentState:
        """Supervisor node that classifies queries."""
        query = state["query"]
        route = self.supervisor.classify_query(query)
        state["route"] = route
        return state
    
    def _it_agent_node(self, state: AgentState) -> AgentState:
        """IT Agent node - processes IT queries using ReadFile and WebSearch tools."""
        print("-> Routing to IT Agent...")
        query = state["query"]
        # Process query with IT agent
        response = self.it_agent.process_query(query)
        state["response"] = response
        return state
    
    def _finance_agent_node(self, state: AgentState) -> AgentState:
        """Finance Agent node - processes Finance queries using ReadFile and WebSearch tools."""
        print("-> Routing to Finance Agent...")
        query = state["query"]
        # Process query with Finance agent
        response = self.finance_agent.process_query(query)
        state["response"] = response
        return state
    
    def _clarification_node(self, state: AgentState) -> AgentState:
        """Clarification node for unclear queries."""
        print("-> Query classification unclear...")
        state["response"] = "I'm not sure which department can help with this query. Could you please provide more details? Are you asking about:\n- Technical/IT issues (computers, software, access, etc.)\n- Financial matters (invoices, expenses, payments, etc.)"
        return state
    
    def process_query(self, query: str) -> str:
        """
        Process a user query through the multi-agent graph.
        
        Args:
            query (str): User's question or request
        Returns:
            str: Final response from the appropriate agent
        """
        # Create initial state
        initial_state: AgentState = {
            "query": query,
            "route": "",
            "response": "",
            "intermediate_steps": []
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Return the response
        return final_state.get("response", "No response generated")
