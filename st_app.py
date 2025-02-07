from PIL import Image
import sys
import re

import streamlit as st

from vectara_agentic.agent import AgentStatusType
from agent import initialize_agent
from config import get_agent_config

initial_prompt = "How can I help you today?"


def format_log_msg(log_msg: str):
    max_log_msg_size = 500
    return log_msg if len(log_msg) <= max_log_msg_size else log_msg[:max_log_msg_size]+'...'

def agent_progress_callback(status_type: AgentStatusType, msg: str):
    output = f'<span style="color:blue;">{status_type.value}</span>: {msg}'
    st.session_state.log_messages.append(output)
    if 'status' in st.session_state:
        latest_message = ''
        if status_type == AgentStatusType.TOOL_CALL:
            match = re.search(r"'([^']*)'", msg)
            tool_name = match.group(1) if match else "Unknown tool"
            latest_message = f"Calling tool {tool_name}..."
        elif status_type == AgentStatusType.TOOL_OUTPUT:
            latest_message = "Analyzing tool output..."
        else:
            return
        
        st.session_state.status.update(label=latest_message)
        
        with st.session_state.status:
            for log_msg in st.session_state.log_messages:
                st.markdown(format_log_msg(log_msg), unsafe_allow_html=True)

@st.dialog(title="Agent logs", width='large')
def show_modal():
    for log_msg in st.session_state.log_messages:
        st.markdown(format_log_msg(log_msg), unsafe_allow_html=True)

async def launch_bot():
    def reset():
        st.session_state.messages = [{"role": "assistant", "content": initial_prompt, "avatar": "🦖"}]
        st.session_state.log_messages = []
        st.session_state.prompt = None
        st.session_state.ex_prompt = None
        st.session_state.first_turn = True
        st.session_state.show_logs = False
        if 'agent' not in st.session_state:
            st.session_state.agent = initialize_agent(cfg, agent_progress_callback=agent_progress_callback)
        else:
            st.session_state.agent.clear_memory()

    if 'cfg' not in st.session_state:
        cfg = get_agent_config()
        st.session_state.cfg = cfg
        st.session_state.ex_prompt = None
        reset()

    cfg = st.session_state.cfg
    print(f'Configuration: {cfg}')

    # left side content

    # Display chat messages
    for message in st.session_state.messages:
        print(f'Message: {message}')
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.write(message["content"])


    # User-provided prompt
    if st.session_state.ex_prompt:
        prompt = st.session_state.ex_prompt
    else:
        prompt = st.chat_input()
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": '🧑‍💻'})
        st.session_state.prompt = prompt
        st.session_state.log_messages = []
        st.session_state.show_logs = False
        with st.chat_message("user", avatar='🧑‍💻'):
            print(f"Starting new question: {prompt}\n")
            st.write(prompt)
        st.session_state.ex_prompt = None
        
    # Generate a new response if last message is not from assistant
    if st.session_state.prompt:
        with st.chat_message("assistant", avatar='🤖'):
            st.session_state.status = st.status('Processing...', expanded=False)
            res = st.session_state.agent.chat(st.session_state.prompt)
            #res = escape_dollars_outside_latex(res)
            res = str(res)
            message = {"role": "assistant", "content": res, "avatar": '🤖'}
            st.session_state.messages.append(message)
            st.markdown(res)


        st.session_state.ex_prompt = None
        st.session_state.prompt = None
        st.session_state.first_turn = False
        st.rerun()



    sys.stdout.flush()