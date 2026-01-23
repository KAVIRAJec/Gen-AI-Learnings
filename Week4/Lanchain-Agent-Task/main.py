"""
Main module for the Langchain Agent Application
"""
import sys
import config_loader
from agent.research_agent import ResearchAgent
def main():
    """Interface for the Langchain Agent Application"""
    try:
        print("\n" + "=" * 70 + "\n")
        print("Langchain Research Agent Application")
        print("\n" + "=" * 70 + "\n")

        # Load configuration
        config_status = config_loader.load_config()
        if config_status:
            print("-> Configuration loaded successfully")
        else:
            print("-> Configuration loading failed")
        
        # Initialize agent
        agent = ResearchAgent()
        if agent:
            print("-> Research Agent initialized successfully\n")
        else:
            print("-> Failed to initialize Research Agent")
            sys.exit(1)
        
        # Main interaction loop
        while True:
            user_query = input("-> Enter your query (type 'exit' to quit): \n").strip()
            if user_query.lower() in ['exit', 'quit']:
                print("-> Exiting the Agent. Goodbye!")
                break
            if not user_query:
                print("-> Please enter a valid query.\n")
                continue
            
            answer = agent.process_query(user_query)
            
            # Display the answer
            print()
            print("-> ANSWER:")
            print(answer)
            print()

    except Exception as e:
        print(f"Error Occurred: {e}")
        sys.exit(1)
    

if __name__ == "__main__":
    main()