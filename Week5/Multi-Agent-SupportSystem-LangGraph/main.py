"""
Main module for the Multi-Agent Support System Application
"""
import sys
import config
from graph.workflow import MultiAgentGraph

def main():
    """Interface for the Multi-Agent Support System Application"""
    try:
        print("\n" + "=" * 70 + "\n")
        print("Multi-Agent Support System with LangGraph")
        print("\n" + "=" * 70 + "\n")

        # Load and validate configuration
        config_status = config.load_config()
        if config_status:
            print("-> Configuration loaded successfully")
        else:
            print("-> Configuration loading failed")
            raise ValueError("Invalid configuration")
        
        # Initialize Multi-Agent Graph with Supervisor
        graph = MultiAgentGraph()
        if graph:
            print("-> Multi-Agent Graph initialized successfully\n")
        else:
            print("-> Failed to initialize Multi-Agent Graph")
            raise ValueError("Graph initialization failed")
        
        # Main interaction loop
        while True:
            user_query = input("-> Enter your query (type 'exit' to quit): \n").strip()
            if user_query.lower() in ['exit', 'quit']:
                print("-> Exiting the application. Goodbye!")
                break
            if not user_query:
                print("-> Please enter a valid query.\n")
                continue
            
            # Process query through the multi-agent graph
            response = graph.process_query(user_query)
            
            # Display the response
            print("-> RESPONSE:")
            print(response)

    except KeyboardInterrupt:
        print("\n-> Application interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error Occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
