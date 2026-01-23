"""
Agent Implemantation for Langchain Agent Application
"""
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_aws import ChatBedrock
from langchain.prompts import PromptTemplate

import config_loader
from mcp.mcp_client import search_google_docs
from rag.hr_search import search_hr_policies
from web_search.search_tool import search_web

class ResearchAgent:
    """Research Agent class for handling queries"""
    
    def __init__(self):
        """Initialize the Research Agent & its components"""  
        self.llm = ChatBedrock(
            model_id=config_loader.BEDROCK_MODEL_ID,
            region_name=config_loader.AWS_REGION,
            credentials_profile_name=None,
            model_kwargs={
                'temperature': 0.0,
                'max_tokens': 4096,
                'stop_sequences': ['\nObservation:']  # Stop after action input
            }
        )

        self.tools = self._define_tools()

        self.agent_executor = self._initialize_agent()
    
    def _define_tools(self):
        """
        Create LangChain tools for the agent
        
        Returns:
            list: List of LangChain Tool objects
        """        
        tools = [
            Tool(
                name="Google_Docs_Search(MCP)",
                func=search_google_docs,
                description=(
                    "Search Google Docs for customer feedback, marketing campaigns, "
                    "insurance claims complaints, and product launch feedback. "
                    "Use this when the query is about customer opinions, feedback, "
                    "surveys, or campaign results. "
                    "Input should be a search query string."
                )
            ),
            Tool(
                name="HR_Policy_Search(RAG)",
                func=search_hr_policies,
                description=(
                    "Search HR policy documents for hiring guidelines, compliance policies, "
                    "AI data handling, GDPR requirements, employee benefits, PTO, vacation, "
                    "health insurance, 401k, and work policies. "
                    "Use this when the query is about internal company policies, HR guidelines, "
                    "compliance rules, employee procedures, or benefits. "
                    "Input should be a search query string."
                )
            ),
            Tool(
                name="Web_Search",
                func=search_web,
                description=(
                    "Search the public internet to retrieve up-to-date, real-world information from any "
                    "relevant online sources. This tool can be used to find facts, explanations, examples, "
                    "definitions, statistics, industry benchmarks, market trends, regulatory updates, "
                    "news articles, documentation, blogs, research papers, forums, and general knowledge. "
                    "Use this tool whenever information is not available in internal documents, is unknown, "
                    "ambiguous, incomplete, or requires external validation. "
                    "You are allowed to explore broadly, refine queries, and search iteratively. "
                    "If the answer is uncertain, use this tool to reduce uncertainty. "
                    "Input must be a concise search query string."
                )
            )
        ]
        print(f"-> Defined {len(tools)} tools for the agent.")
        return tools

    def _initialize_agent(self) -> AgentExecutor:
        """Set up the agent with necessary tools and configurations"""

        template = """Answer the following question as best you can. You have access to the following tools:

{tools}

Use the following format EXACTLY:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (a simple search query string, NOT an explanation)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT FORMATTING RULES:
- Action Input must be a simple query string only, not a sentence or explanation
- Each line must start with exactly one of: Question, Thought, Action, Action Input, Observation, or Final Answer
- After "Action:", the next line MUST be "Action Input:"
- After "Thought:", the next line MUST be "Action:" or "Final Answer:"

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

        prompt = PromptTemplate(template=template,
                                input_variables=["input", "agent_scratchpad", "tools", "tool_names"])
        
        # Create ReAct agent
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
            max_iterations=5,
            handle_parsing_errors=True,
            return_intermediate_steps=False
        )

        return agent_executor
    
    def process_query(self, query: str) -> str:
        """Process a user query and return the agent's response
        
        Args:
            query (str): The user query to process
        Returns:
            str: The response from the agent
        """
        response = self.agent_executor.invoke({"input": query})

        intermediate_steps = response.get("intermediate_steps", [])
        for i, step in enumerate(intermediate_steps, start=1):
            action, observation = step
            print(f"Step {i} \n")
            print(f"Tool: {action.tool} \n")
            print(f"Tool Input: {action.tool_input} \n")
            print(f"Observation: {observation} \n")

        return response.get("output", "No response generated by the agent.")