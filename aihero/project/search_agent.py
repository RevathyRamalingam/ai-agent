import search_tool
from pydantic_ai import Agent

SYSTEM_PROMPT_TEMPLATE = """
You are a helpful assistant that answers questions about documentation.  

Use the search tool to find relevant information from the repository before answering questions.  

If you can find specific information through search, use it to provide accurate answers.

Always include references by citing the filename of the source material you used.
Replace it with the full path to the GitHub repository:
"https://github.com/{repo_owner}/{repo_name}/blob/main/"
Format: [LINK TITLE](FULL_GITHUB_LINK)


If the search doesn't return relevant results, provide general guidance.
"""
def init_agent(index, repo_owner,repo_name):
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(repo_owner=repo_owner,repo_name=repo_name)
    #print("System Prompt:",system_prompt)
    s_tool = search_tool.SearchTool(index=index)
    print("Search Tool:",s_tool)
    agent = Agent(
        name="gh_agent",
        instructions=system_prompt,
        tools=[s_tool.search],
        model='gpt-4o-mini'
    )   
    print("Agent initiaized is :",agent)
    return agent