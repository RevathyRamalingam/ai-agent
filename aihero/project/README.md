                            Code Repository QA Assistant

This project Code Repository QA Assistant aims to build an AI Agent similar to DeepWiki that can answer queries about your repository. So make sure to set the OPENAI_API_KEY in the environment variables and make sure your repository has enough documentation.

This QA Assistant uses hybrid search to answer questions about your repository. It uses the search tool to find relevant information from the repository before answering questions. It also gives the source code of the repository as a reference.

## Folder

1. aihero/project - The folder that contains the AI Agent
2. aihero/project/eval - The folder that contains the evaluation files
3. aihero/project/eval/data-gen.py - The file that generates the data for evaluation
4. aihero/project/eval/evaluations.py - The file that contains the evaluation files
5. aihero/project/screenshot - The folder that contains the screenshots of the FAQ AI Assistant
6. aihero/project/requirements.txt - The file that contains the requirements for the project to build

## Files

1. main.py - The main file that runs the AI Agent
2. ingest.py - The file that ingests the data from the repository
3. search_tool.py - The file that contains the search tool
4. search_agent.py - The file that contains the search agent
5. logs.py - The file that contains the logs

## How to run the project

1. Clone the repository
2. pip install -r requirements.txt
3. Make sure to set the OPENAI_API_KEY in the environment variables 
4. Run the app.py file that opens an interactive streamlit UI where the user can ask questions about the repository

    uv run streamlit run app.py 

    The browser opens at Local URL: http://localhost:8501 to answer your questions about the GITHUB repository of your choice
    You can also run locally using the below command

    uv run python main.py    This can start the agent locally in your machine and you can ask it questions about your repository

5. The AI Agent will start running and you can ask it questions about your repository
6. The AI Agent will answer your questions
7. The AI Agent will also provide you with the source code of the repository

## Demo

A demo of how to run the project can be found at https://www.loom.com/share/2ee693c8b719471193b97a132e618486

## Future Scope

Currently this project works for all GitHub repositories. In the future, we can extend this to other version control systems like GitLab and Bitbucket or even local repositories.

## Acknowledgement

Thanks to Alexey Grigorev for the course on AI Agents. This course was very helpful in building this project that creates an AI Agent from scratch using PydanticAI APIs, uses minsearch python library for hybrid search and uses Streamlit to create an interactive UI.   
