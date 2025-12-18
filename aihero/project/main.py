import ingest
import search_tool
import logs
import search_agent
import asyncio

REPO_OWNER="RevathyRamalingam"
REPO_NAME="machinelearning"

def initialize_index():
    print(f"Starting FAQ AI Assistant for {REPO_OWNER}/{REPO_NAME}")
    print("Initializing DataIngestion...")
    def filter(doc):
        return 'data-engineering' in doc['filename']
    index = ingest.index_data(REPO_OWNER,REPO_NAME)
    print("Data Indexing done successfully")
    return index

def initialize_agent(index):
    print("Agent initialization started..")
    agent = search_agent.init_agent(index,REPO_OWNER,REPO_NAME)
    print("Agent Initialization completed..")
    return agent

def main():
    print("Welcome to FAQ Agent developed by Revathy!")
    index=initialize_index()
    agent = initialize_agent(index)
    print("Now the Agent is ready to answer your queries")
    print("Type 'stop' to exit the program")

    while True:
        question = input("Your question:")
        if (question.strip().lower() == 'stop'):
            print("goodbye!!")
            break
        print("Processing your question")
        response = asyncio.run(agent.run(user_prompt=question))
        logs.log_interaction_to_file(agent,response.new_messages())
        print("\nResponse is \n",response.output)


if __name__ == "__main__":
    main()
