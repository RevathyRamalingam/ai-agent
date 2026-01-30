import streamlit as st
import ingest
import search_tool
import logs
import search_agent
import asyncio

# Configure page
st.set_page_config(
    page_title="CodeRepository QA Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'index' not in st.session_state:
    st.session_state.index = None
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'repo_owner' not in st.session_state:
    st.session_state.repo_owner = ""
if 'repo_name' not in st.session_state:
    st.session_state.repo_name = ""

def initialize_index(repo_owner, repo_name):
    """Initialize the data index"""
    with st.spinner(f"Initializing data ingestion for {repo_owner}/{repo_name}..."):
        index = ingest.index_data(repo_owner, repo_name)
        st.success("Data indexing completed successfully!")
        return index

def initialize_agent(index, repo_owner, repo_name):
    """Initialize the search agent"""
    with st.spinner("Initializing AI agent..."):
        agent = search_agent.init_agent(index, repo_owner, repo_name)
        st.success("Agent initialized successfully!")
        return agent

def main():
    # Header
    st.title("🤖 CodeRepository QA Assistant")
    if st.session_state.initialized:
        st.markdown(f"### Repository: `{st.session_state.repo_owner}/{st.session_state.repo_name}`")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.info("This QA assistant helps you find answers about any GITHUB Code repository.")
        st.markdown("**Developer:** Revathy Ramalingam")
        
        # Initialization inputs
        if not st.session_state.initialized:
            st.session_state.repo_owner = st.text_input("GitHub Username", value=st.session_state.repo_owner)
            st.session_state.repo_name = st.text_input("Repository Name", value=st.session_state.repo_name)
            
            if st.button("🚀 Initialize Agent", use_container_width=True, disabled=not (st.session_state.repo_owner and st.session_state.repo_name)):
                try:
                    st.session_state.index = initialize_index(st.session_state.repo_owner, st.session_state.repo_name)
                    st.session_state.agent = initialize_agent(st.session_state.index, st.session_state.repo_owner, st.session_state.repo_name)
                    st.session_state.initialized = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error during initialization: {str(e)}")
        else:
            st.success("✅ Agent Ready")
            if st.button("🔄 Reset Agent", use_container_width=True):
                st.session_state.index = None
                st.session_state.agent = None
                st.session_state.messages = []
                st.session_state.initialized = False
                st.rerun()
        
        # Clear conversation button
        if st.session_state.initialized and st.session_state.messages:
            if st.button("🗑️ Clear Conversation", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
    
    # Main content area
    if not st.session_state.initialized:
        st.info("👈 Please initialize the agent from the sidebar to get started.")
        st.markdown("""
        ### How to use:
        1. Click **Initialize Agent** in the sidebar
        2. Wait for the initialization to complete
        3. Start asking your questions in the chat!
        """)
    else:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask your question here..."):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get agent response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = asyncio.run(st.session_state.agent.run(user_prompt=prompt))
                        logs.log_interaction_to_file(st.session_state.agent, response.new_messages())
                        answer = response.output
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        error_msg = f"Sorry, I encountered an error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
