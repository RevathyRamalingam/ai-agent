import search_tool
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

groq_model = GroqModel(
    model_name="llama-3.1-8b-instant",  # or llama3-70b-8192
)

SYSTEM_PROMPT_TEMPLATE = """
You are a helpful assistant that answers questions about documentation.  

Use the search tool to find relevant information from the document before answering questions.  

If you can find specific information through search, use it to provide accurate answers.

If the search doesn't return relevant results, notify the user.
"""
def init_agent(index):
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format()
    #print("System Prompt:",system_prompt)
    s_tool = search_tool.SearchTool(index=index)
    print("Search Tool:",s_tool)
    agent = Agent(
        name="gh_agent",
        instructions=system_prompt,
        tools=[s_tool.search],
        model=groq_model
    )   
    print("Agent initialized is :",agent)
    return agent