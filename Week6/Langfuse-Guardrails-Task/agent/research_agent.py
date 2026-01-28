"""
Research Agent with LangFuse Tracing and Guardrails AI
"""

import os
import logging
import warnings

# Suppress all warnings and errors
os.environ['GRPC_ENABLE_FORK_SUPPORT'] = '1'
warnings.filterwarnings("ignore")
logging.getLogger("opentelemetry").setLevel(logging.CRITICAL)
logging.getLogger("guardrails").setLevel(logging.CRITICAL)

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_aws import ChatBedrock
from langchain.prompts import PromptTemplate
from langfuse.langchain import CallbackHandler
from langfuse import get_client

import config
from tools.web_search import search_web
from tools.rag_search import search_documents
from validators.guardrails_validator import GuardrailsValidator

class ResearchAgent:
    """Research Agent with LangFuse tracing and Guardrails AI"""
    
    def __init__(self):
        print("-> Initializing Research Agent...")
        
        # Initialize LangFuse callback
        self.langfuse_handler = None
        if all([config.LANGFUSE_PUBLIC_KEY, config.LANGFUSE_SECRET_KEY]):
            try:
                langfuse = get_client()
                self.langfuse_handler = CallbackHandler()
                print("-> LangFuse tracing enabled (batched mode)")
            except Exception as e:
                print(f"-> WARNING: LangFuse initialization failed: {e}")
                self.langfuse_handler = None
        else:
            print("-> LangFuse tracing disabled (no credentials)")
        
        # Initialize Guardrails
        self.guardrails = GuardrailsValidator()
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Define tools
        self.tools = self._define_tools()
        
        # Initialize agent
        self.agent_executor = self._initialize_agent()
        
        print("-> Research Agent initialized successfully")

    def _initialize_llm(self):
        """Initialize LLM with LangFuse callback"""
        return ChatBedrock(
            model_id=config.MODEL_ID,
            region_name=config.AWS_REGION,
            model_kwargs={
                'temperature': config.TEMPERATURE,
                'max_tokens': 4096,
                'stop_sequences': ['\nObservation:']
            },
            callbacks=[self.langfuse_handler] if self.langfuse_handler else None
        )
    
    def _define_tools(self):
        """Define tools for the agent"""
        tools = [
            Tool(
                name="Document_Search",
                func=search_documents,
                description=(
                    "Search internal documents for information about company policies, "
                    "HR guidelines, procedures, and internal documentation. "
                    "Use when query is about internal company information. "
                    "Input: search query string."
                )
            ),
            Tool(
                name="Web_Search",
                func=search_web,
                description=(
                    "Search the internet for general knowledge, current information, "
                    "research topics, definitions, explanations, and facts. "
                    "Use when information is not in internal documents. "
                    "Input: search query string."
                )
            )
        ]
        print(f"-> Defined {len(tools)} tools")
        return tools
    
    def _initialize_agent(self) -> AgentExecutor:
        """Set up the ReAct agent"""
        
        template = """Answer the following question as best you can. You have access to the following tools:

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

        Begin!

        Question: {input}
        Thought: {agent_scratchpad}"""

        prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
            template=template
        )
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            callbacks=[self.langfuse_handler] if self.langfuse_handler else None,
            return_intermediate_steps=True
        )
        
        return agent_executor
    
    def process_query(self, query: str) -> dict:
        """Process query with LangFuse tracing and Guardrails AI validation"""
        try:
            # Input validation
            input_validation = self.guardrails.validate_input(query)
            if not input_validation["allowed"]:
                return {
                    "output": input_validation["message"],
                    "intermediate_steps": [],
                    "success": True,
                    "guardrails_triggered": True,
                    "guardrails_reason": input_validation["reason"]
                }
            
            # Execute agent
            config = {"run_name": f"Query: {query[:60]}", "metadata": {"query": query}}
            result = self.agent_executor.invoke(
                {"input": query}, 
                config={"callbacks": [self.langfuse_handler] if self.langfuse_handler else None, "config": config}
            )
            
            output = result.get("output", "No response generated")
            
            # Output validation
            output_validation = self.guardrails.validate_output(output)
            
            return {
                "output": output_validation["modified_output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True,
                "guardrails_triggered": not output_validation["allowed"],
                "guardrails_reason": output_validation["reason"]
            }
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(f"-> {error_msg}")
            return {
                "output": error_msg,
                "intermediate_steps": [],
                "success": False
            }
