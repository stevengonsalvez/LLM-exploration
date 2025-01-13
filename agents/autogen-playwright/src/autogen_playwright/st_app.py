"""
This is a demo of AutoGen chat agents. You can use it to chat with OpenAI's GPT-3 and GPT-4 models. They are able to execute commands, answer questions, and even write code.
An example a question you can ask is: 'How is the S&P 500 doing today? Summarize the news for me.'
UserProxyAgent is used to send messages to the AssistantAgent. The AssistantAgent is used to send messages to the UserProxyAgent.

"""


from autogen_playwright.prompts.prompts import WEB_TESTER_PROMPT
import streamlit as st
import asyncio
from autogen import AssistantAgent, UserProxyAgent
import os

# setup page title and description
st.set_page_config(page_title="AutoGen Chat app", page_icon="🤖", layout="wide")

# Add custom CSS for the chat container
st.markdown("""
    <style>
    .chat-container {
        height: 600px;
        overflow-y: auto;
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("🤖 **Synthetic Testing Agent**")
st.markdown("""
This is an automated testing agent that converts plain English instructions into executable test steps. 

Format your test steps either:
- One step per line
- As comma-separated steps

Examples:
```
go to google.com, search for playwright, click first result

OR

go to google.com
search for playwright
click first result
```
""")
st.markdown("Start by providing your OpenAI API key in the sidebar →")


class TrackableAssistantAgent(AssistantAgent):
    """
    A custom AssistantAgent that tracks the messages it receives.

    This is done by overriding the `_process_received_message` method.
    """

    def _process_received_message(self, message, sender, silent):
        with chat_history:
            with st.chat_message(sender.name):
                st.markdown(message)
        return super()._process_received_message(message, sender, silent)


class TrackableUserProxyAgent(UserProxyAgent):
    """
    A custom UserProxyAgent that tracks the messages it receives.

    This is done by overriding the `_process_received_message` method.
    """

    def _process_received_message(self, message, sender, silent):
        with chat_history:
            with st.chat_message(sender.name):
                st.markdown(message)
        return super()._process_received_message(message, sender, silent)


# add placeholders for selected model and key
selected_model = None
selected_key = None

# setup sidebar: models to choose from and API key input
with st.sidebar:
    st.header("LLM Configuration")
    llm_provider = st.selectbox("Provider", ["OpenAI", "Anthropic", "Cerebras"], index=0)
    
    if llm_provider == "OpenAI":
        selected_model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4-1106-preview", "gpt-4o"], index=1)
        st.markdown("Press enter to save key")
        st.markdown(
            "For more information about the models, see [here](https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo)."
        )
        selected_key = st.text_input("OpenAI API Key", type="password")
        # Set environment variable for OpenAI
        os.environ["OPENAI_API_KEY"] = selected_key
    elif llm_provider == "Anthropic":
        selected_model = st.selectbox("Model", ["claude-3-opus-20240229", "claude-3-sonnet-20240229"], index=0)
        st.markdown("Press enter to save key")
        st.markdown(
            "For more information about Claude models, see [here](https://docs.anthropic.com/claude/docs/models-overview)."
        )
        selected_key = st.text_input("Anthropic API Key", type="password")
        # Set environment variable for Anthropic
        os.environ["ANTHROPIC_API_KEY"] = selected_key
    else:  # Cerebras
        selected_model = st.selectbox("Model", ["llama3.3-70b", "llama3.1-70b"], index=0)
        st.markdown("Press enter to save key")
        st.markdown(
            "For more information about Cerebras models, see [here](https://www.cerebras.net/blog/cerebras-llama-70b)."
        )
        selected_key = st.text_input("Cerebras API Key", type="password")
        # Set environment variable for Cerebras
        os.environ["CEREBRAS_API_KEY"] = selected_key

# setup main area: user input and chat messages
chat_container = st.container()
with chat_container:
    # Create a container for the chat history with a fixed height
    chat_history = st.container()
    
    # Add a horizontal line to separate chat and input
    st.markdown("---")
    
    # Create the input area at the bottom
    user_input = st.text_area("Your message", height=100, key="user_input")
    
    # Split input either by commas or newlines
    if "," in user_input:
        steps = [step.strip() for step in user_input.split(",")]
    else:
        steps = [step.strip() for step in user_input.splitlines() if step.strip()]
        
    steps_formatted = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
    
    test_message = f"""
    Execute the following test scenario:
    
    Test Scenario: web page navigation and validation
    
    Steps:
    {steps_formatted}
    
    Important:
    - Maximum 5 retries for any action
    - Take screenshots at key steps
    - Provide detailed error information if steps fail
    - Generate a test summary at the end
    - Always end with a TERMINATE message
    """

    
    # Add a submit button
    if st.button("Send", type="primary"):
        if not user_input:  # Skip if user input is empty
            st.stop()
            
        if not selected_key or not selected_model:
            st.warning("You must provide valid API key and choose preferred model", icon="⚠️")
            st.stop()
            
        # setup request timeout and config list
        if llm_provider == "OpenAI":
            config = {
                "model": selected_model,
                "api_key": selected_key,
                "timeout": 600,
                "max_tokens": 2000,
                "api_type": "openai"
            }
        elif llm_provider == "Anthropic":
            config = {
                "model": selected_model,
                "api_key": selected_key,
                "timeout": 600,
                "max_tokens": 2000,
                "api_type": "anthropic"
            }
        else:  # Cerebras
            config = {
                "model": selected_model,
                "api_key": selected_key,
                "timeout": 600,
                "max_tokens": 2000,
                "api_type": "cerebras"
            }
            
        llm_config = {
            "config_list": [config],
            "seed": 42,  # seed for reproducibility
            "temperature": 0  # temperature of 0 means deterministic output
        }
        # create an AssistantAgent instance named "assistant"
        assistant = TrackableAssistantAgent(name="assistant", system_message=WEB_TESTER_PROMPT, llm_config=llm_config)

        # create a UserProxyAgent instance named "user"
        # human_input_mode is set to "NEVER" to prevent the agent from asking for user input
        user_proxy = TrackableUserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            llm_config=llm_config,
            is_termination_msg=lambda x: x.get("content", "").strip().endswith("TERMINATE") or any(phrase in x.get("content", "") for phrase in ["Test Summary", "If you have any further questions", "The execution succeeded"]),
            code_execution_config={
                "use_docker": False
            }
        )

        # Create an event loop: this is needed to run asynchronous functions
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Define an asynchronous function: this is needed to use await
        if "chat_initiated" not in st.session_state:
            st.session_state.chat_initiated = False  # Initialize the session state

        if not st.session_state.chat_initiated:

            async def initiate_chat():
                await user_proxy.a_initiate_chat(
                    assistant,
                    message=user_input,
                    max_consecutive_auto_reply=2,
                    max_turns=3,
                    is_termination_msg=lambda x: x.get("content", "").strip().endswith("TERMINATE") or any(phrase in x.get("content", "") for phrase in ["Test Summary", "The execution succeeded"]),
                )
                st.stop()  # Stop code execution after termination command

            # Run the asynchronous function within the event loop
            loop.run_until_complete(initiate_chat())

            # Close the event loop
            loop.close()

            st.session_state.chat_initiated = True  # Set the state to True after running the chat


# stop app after termination command
st.stop()