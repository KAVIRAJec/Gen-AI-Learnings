"""
Main Module - Week 6 LangFuse Guardrails Task
"""

import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

import sys
import config
from agent.research_agent import ResearchAgent


def interactive_mode(agent: ResearchAgent):
    """Interactive query loop"""
    while True:
        user_query = input("\n-> Enter your query: ").strip()
        
        if user_query.lower() in ['exit', 'quit']:
            print("\n-> Goodbye!")
            break
        
        if not user_query:
            print("-> Please enter a query")
            continue
        
        # Process query
        result = agent.process_query(user_query)
        
        # Display result
        print("\n" + "="*70)
        print("RESPONSE")
        print("="*70)
        print(result["output"])
        print("="*70)


def main():
    """Main entry point"""
    print("#"*70)
    print("WEEK 6: LANGFUSE GUARDRAILS TASK")
    print("#"*70)
    
    # Load configuration
    print("-> Loading configuration...")
    if not config.load_config():
        print("-> ERROR: Configuration failed")
        sys.exit(1)
    print("-> Configuration loaded\n")
    
    # Initialize agent
    print("-> Initializing agent...")
    try:
        agent = ResearchAgent()
    except Exception as e:
        print(f"-> ERROR: Failed to initialize agent: {e}")
        sys.exit(1)
    
    print("\n-> Agent ready!\n")
    
    interactive_mode(agent)

if __name__ == "__main__":
    main()
