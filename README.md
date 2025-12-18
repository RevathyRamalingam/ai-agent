# AI-Agent
 An AI agent is a software entity that utilizes artificial intelligence techniques to perform tasks autonomously, or with minimal human intervention. These agents can perceive their environment through sensors, reason about the information they gather, and take actions to achieve specific goals.

Key characteristics of AI agents include:

1. **Autonomy**: They can operate independently and make decisions without human input.
2. **Reactivity**: They can respond to changes in their environment in real-time.
3. **Proactiveness**: They can take initiative to fulfill goals or improve their own performance.
4. **Social ability**: They can interact with other agents and humans, often communicating and collaborating to achieve complex tasks.

AI agents can be found in various applications, such as virtual personal assistants (like Siri or Alexa), self-driving cars, gaming NPCs (non-player characters), and robotic systems.


This project AI-Agent aims to build anAI Agent similar to DeepWiki that can answer queries about your repository.

## Folder

1. aihero - The main folder that contains the AI Agent
2. aihero/project - The folder that contains the AI Agent
3. aihero/project/eval - The folder that contains the evaluation files
4. aihero/project/eval/data-gen.py - The file that generates the data for evaluation
5. aihero/project/eval/evaluations.py - The file that contains the evaluation files
6. aihero/screenshot - The folder that contains the screenshots of the FAQ AI Assistant
7. aihero/course - The folder that contains the course files
8. aihero/course/requirements.txt - The file that contains the requirements for the project to build

##Files

1. main.py - The main file that runs the AI Agent
2. ingest.py - The file that ingests the data from the repository
3. search_tool.py - The file that contains the search tool
4. search_agent.py - The file that contains the search agent
5. logs.py - The file that contains the logs

## How to run the AI Agent

1. Clone the repository
2. pip install -r requirements.txt
3. Make sure to set the OPENAI_API_KEY in the environment variables 
4. Run the main.py file
    uv run streamlit run app.py
5. The AI Agent will start running and you can ask it questions about your repository
6. The AI Agent will answer your questions
7. The AI Agent will also provide you with the source code of the repository

## Acknowledgement

Thanks to Alexey Grigorev for the course on AI Agents. If you are someone who is interested in AI Agents like me, I highly recommend his course. It's completely free.
