import ingest 
import search_tool 
import logs 
import search_agent
import asyncio
import logging
logging.basicConfig(level=logging.DEBUG)

def initialize_index(url_path):
    print(f"Starting document QA Assistant for {url_path}")
    print("Initializing DataIngestion...")
    index = ingest.index_data(url_path,chunk=True)
    print("Data Indexing done successfully")
    return index

def initialize_agent(index):
    print("Agent initialization started..")
    agent = search_agent.init_agent(index)
    print("Agent Initialization completed..")
    return agent

def main():
    print("Welcome to document QA Assistant")
    url_path = input("Enter url path : ")
    index = initialize_index(url_path)
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
