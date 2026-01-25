"""
Finance Agent Implementation for Multi-Agent Support System
"""

import sys
import os

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_aws import ChatBedrock
from langchain.prompts import PromptTemplate
import config
from tools.rag.finance_search import search_finance_documents
from tools.web_search import search_web

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FinanceAgent:
    """
    Finance Agent for handling financial policy and expense queries.
    
    This agent uses two tools:
    1. ReadFile (RAG) - Search Finance policy documents
    2. WebSearch - Search the web for additional information
    """
    
    def __init__(self):
        """Initialize the Finance Agent with LLM, tools, and agent executor"""
        print("-> Initializing Finance Agent...")
        
        self.llm = ChatBedrock(
            model_id=config.MODEL_ID,
            region_name=config.AWS_REGION,
            credentials_profile_name=None,
            model_kwargs={
                'temperature': 0.0,
                'max_tokens': 4096,
                'stop_sequences': ['\nObservation:']  # Stop after action input
            }
        )
        
        # Define tools
        self.tools = self._define_tools()
        
        # Initialize agent executor
        self.agent_executor = self._initialize_agent()
        
        print("-> Finance Agent initialized successfully")
    
    def _define_tools(self):
        """
        Create LangChain tools for the Finance agent
        
        Returns:
            list: List of LangChain Tool objects
        """
        tools = [
            Tool(
                name="ReadFile_Finance_Documents",
                func=search_finance_documents,
                description=(
                    "Search and retrieve information from internal Finance policy documents. "
                    "Covers: expense reimbursement policies, budget guidelines, invoice processing, "
                    "payment procedures, financial reporting, cost center allocations, "
                    "travel expense policies, vendor payment terms, and financial approval workflows. "
                    "ALWAYS use this tool FIRST to check internal financial policies. "
                    "Input: a specific search query string (e.g., 'expense reimbursement limits')"
                )
            ),
            Tool(
                name="WebSearch",
                func=search_web,
                description=(
                    "Search the internet for financial regulations, tax information, accounting standards, "
                    "best practices, financial definitions, and general financial knowledge. "
                    "Use this tool when: (1) internal documents don't have enough information, "
                    "(2) you need current tax rates or regulations, (3) finding industry standards, "
                    "(4) getting additional context or financial definitions. "
                    "Input: a concise search query (e.g., 'corporate expense tax deductibility 2026')"
                )
            )
        ]
        
        print(f"-> Defined {len(tools)} tools for Finance Agent")
        return tools
    
    def _initialize_agent(self) -> AgentExecutor:
        """
        Set up the ReAct agent with tools and prompt template
        Returns:
            AgentExecutor: Configured agent executor
        """
        # Define the ReAct prompt template
        template = """You are a Finance support specialist. Answer financial policy questions by using BOTH available tools when needed.

        You have access to the following tools:

        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        IMPORTANT - Tool Usage Strategy:
        1. ALWAYS start with ReadFile_Finance_Documents to check internal policies
        2. If information is insufficient, incomplete, or you need additional context, ALWAYS use WebSearch
        3. For expense or policy questions, use BOTH tools to provide comprehensive answers
        4. Combine information from both sources in your final answer when relevant

        Begin!

        Question: {input}
        Thought: {agent_scratchpad}"""

        prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
            template=template
        )
        
        # Create the ReAct agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        return agent_executor
    
    def process_query(self, query: str) -> str:
        """
        Process a Finance query using the agent
        
        Args:
            query (str): User's Finance question
            
        Returns:
            str: Agent's response
        """
        print(f"\n-> Processing Finance query: {query}")
        
        try:
            result = self.agent_executor.invoke({"input": query})
            
            # Extract the final answer
            answer = result.get("output", "No response generated")
            return answer
            
        except Exception as e:
            error_msg = f"Error processing Finance query: {str(e)}"
            print(f"-> {error_msg}")
            return error_msg
