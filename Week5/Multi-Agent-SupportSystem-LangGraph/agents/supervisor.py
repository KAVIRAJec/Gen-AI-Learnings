"""
Supervisor Agent for Multi-Agent Support System.
Routes user queries to appropriate specialist agents (IT or Finance).
"""

import sys
import os
from typing import Literal
from typing_extensions import TypedDict

from langchain.agents import AgentExecutor, create_react_agent
from langchain_aws import ChatBedrock
from langchain.prompts import PromptTemplate
import config

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define the state structure for LangGraph
class AgentState(TypedDict):
    """
    State structure for the multi-agent system.
    This is passed between nodes in the LangGraph workflow.
    """
    query: str              # User's original query
    route: str              # Routing decision: "IT", "FINANCE", or "UNCLEAR"
    response: str           # Final response from specialist agent
    intermediate_steps: list  # Steps taken during processing


class SupervisorAgent:
    """
    Supervisor Agent that classifies queries and routes to specialist agents.
    """
    
    def __init__(self):
        print("-> Initializing Supervisor Agent...")
        
        self.llm = ChatBedrock(
            model_id=config.MODEL_ID,
            model_kwargs={
                "temperature": config.TEMPERATURE,
                "max_tokens": 2096,
                'stop_sequences': ['\nObservation:']  # Stop after action input
            },
            region_name=config.AWS_REGION,
            credentials_profile_name=None,
        )
        
        # Define tools (none needed for classification)
        self.tools = []
        
        # Define the supervisor's ReAct prompt for classification
        self.supervisor_prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
            template="""You are a Supervisor Agent in a multi-agent support system that routes queries to specialist agents.

Your task is to analyze the user's query and determine which specialist agent should handle it:

1. IT Agent - For queries about:
   - Technical issues, software, hardware
   - Networks, passwords, access control
   - Systems, applications, email, computers, servers
   - VPN, security, technical support

2. Finance Agent - For queries about:
   - Invoices, payments, expenses, budgets
   - Accounting, financial reports, purchase orders
   - Reimbursements, salaries, payroll
   - Financial policies and procedures

3. UNCLEAR - If the query doesn't clearly fit into IT or Finance categories

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must classify
Thought: analyze the query to determine which category it belongs to
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: Return ONLY one word - IT, FINANCE, or UNCLEAR

Begin!

Question: {input}
Thought: {agent_scratchpad}"""
        )
        
        # Create the ReAct agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.supervisor_prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=3
        )
        
        print("-> Supervisor Agent initialized successfully")
    
    def classify_query(self, query: str) -> str:
        """
        Classify a user query using the ReAct agent.
        
        Args:
            query (str): User's question or request
            
        Returns:
            str: Routing decision - "IT", "FINANCE", or "UNCLEAR"
        """
        print(f"-> Classifying query: {query[:50]}...")
        
        try:
            result = self.agent_executor.invoke({"input": query})
            
            # Extract the classification from the agent's output
            classification = result.get("output", "UNCLEAR").strip().upper()
            
            # Validate classification result
            if classification not in ["IT", "FINANCE", "UNCLEAR"]:
                print(f"-> Warning: Unexpected classification '{classification}', defaulting to UNCLEAR")
                classification = "UNCLEAR"
            
            print(f"-> Query classified as: {classification}")
            return classification
            
        except Exception as e:
            print(f"-> Error during classification: {str(e)}")
            return "UNCLEAR"
    
    def route_query(self, state: AgentState) -> Literal["IT", "FINANCE", "UNCLEAR"]:
        """
        Route a query to the appropriate specialist agent.
        
        This is the main method used by LangGraph for routing decisions.
        It processes the state and returns the routing decision.
        
        Args:
            state (AgentState): Current state with query information
            
        Returns:
            str: "IT", "FINANCE", or "UNCLEAR" for LangGraph routing
        """
        query = state["query"]
        classification = self.classify_query(query)
        
        # Update state with routing decision
        state["route"] = classification
        
        return classification

