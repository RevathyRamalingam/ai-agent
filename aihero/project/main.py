import ingest 
import search_tool 
import logs 
import search_agent
import asyncio

def initialize_index(repo_owner, repo_name):
    print(f"Starting CodeRepository QA Assistant for {repo_owner}/{repo_name}")
    print("Initializing DataIngestion...")
    index = ingest.index_data(repo_owner, repo_name,chunk=True)
    print("Data Indexing done successfully")
    return index

def initialize_agent(index, repo_owner, repo_name):
    print("Agent initialization started..")
    agent = search_agent.init_agent(index, repo_owner, repo_name)
    print("Agent Initialization completed..")
    return agent

def main():
    print("Welcome to CodeRepository QA Assistant developed by Revathy Ramalingam!")
    repo_owner = input("Enter your GitHub username: ")
    repo_name = input("Enter your GitHub repository name: ")
    index = initialize_index(repo_owner, repo_name)
    agent = initialize_agent(index, repo_owner, repo_name)
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
