import streamlit as st
import requests
from api import ImpaxAIRAAPI
import uuid
import pandas as pd
import numpy as np
from pathlib import Path
import shutil
import utils


st.set_page_config(
    page_title="Impax AI Assistant Demo",
    layout="wide",
    page_icon="logo.png")

company_analysis_databases = []
SECTIONS = ["Introduction", "Impax Investment Assistant", "Research Search", 
            "10 Step Writing", "Feedback"]
industry_knowledgebase_databases = [
    "knowledge_base_semiconductors",
    "knowledge_base_ev"
    ]

def chat_engine():
    
    chat_tab, chat_with_uploads_tab = st.tabs(["Chat Assistant", "Upload File and Chat"])
    with chat_tab:
        st.header("Impax Chat Assistant")
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        with st.form( key="user_chat_input"):
            input = st.text_area("Enter your questions here: ")
            submit_button = st.form_submit_button(label='Submit')
            if submit_button and input:
                response = ImpaxAIRAAPI.chat(
                    session_id=st.session_state.session_id, 
                    question=input)
                reply = response.get("response", "No response from assistant")

                st.session_state.chat_history.append({
                    "user_input": input,
                    "assistant_reply": reply,
                    "sources": response.get("sources", ["no reply received"]),
                    "tools_used": response.get("tools_used", ["no tools were used"]),
                    "raw_contents": response.get("raw_contents", ["no raw contents retrieved"])
                })
        
        clear_chat = st.button("Clear current chat", key="clear_current_chat")
        chat_messages_container = st.container()
        if clear_chat:
            ImpaxAIRAAPI.clear_chat_session(st.session_state.session_id)
            st.session_state.chat_history.pop()
            del st.session_state.session_id
            st.info("Chat has been cleared.") 
            chat_messages_container.write("")
        # Display chat history in descending order
        with chat_messages_container:
            for i, chat_message in enumerate(reversed(st.session_state.chat_history)):
                col1, col2 = st.columns([2, 3]) 
                with col1:
                    st.markdown(f"### User message:\n{chat_message['user_input']}")
                    st.markdown(f"### Assistant reply:\n{chat_message['assistant_reply']}")
                    st.markdown("---")  # Optional: Adds a line for better separation
                with col2:
                    st.markdown("### Source:")
                    sources_df = pd.DataFrame(chat_message['sources'])
                    st.dataframe(sources_df)

                    st.markdown("------\n")
                    st.markdown("### Tools used by the assistant:")
                    st.markdown("- " + "- ".join([f"`{t.strip()}`\n" for t in chat_message.get("tools_used")]))

                    st.markdown("------\n")
                    st.markdown("### Show raw content:")
                    show_raw_content = st.button("Show raw content", key=f"show_raw_content_chat_button_{i}")
                    hide_raw_content = st.button("Hide raw content", key=f"hide_raw_content_chat_button_{i}")
                    raw_content_containers = []
                    raw_content_containers.append(st.empty())
                    if show_raw_content:
                        raw_content_containers[i].write("\n".join(chat_message.get("raw_contents")))
                    if hide_raw_content:
                        raw_content_containers[i].write("")
                st.divider()

    with chat_with_uploads_tab:
        st.header("Impax Investment Chat Assistant")
        st.subheader("Chat with uploaded files")
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())


        with st.form( key="user_chat_input_with_upload"):
            input = st.text_area("Enter your questions here: ")
            submit_button = st.form_submit_button(label='Submit')
            files_uploaded = st.file_uploader(
                    "upload your files here",
                    key="chat_file_uploader",
                    accept_multiple_files=True
                )
            if submit_button and input:
                
                save_path_root = f"./temp/uploads/{st.session_state.session_id}"
                save_path_root_obj = Path(save_path_root)
                if not save_path_root_obj.exists():
                    save_path_root_obj.mkdir(parents=True)
                if files_uploaded:
                    files_stream=[file.read() for file in files_uploaded]
                    # for file in files_uploaded:
                    #     save_path = save_path_root_obj.joinpath(file.name)
                    #     with open(save_path, "wb") as f:
                    #         f.write(file.read())
                    #         f.close()
                    response = ImpaxAIRAAPI.chat_with_uploads(
                        session_id=st.session_state.session_id, 
                        question=input,
                        files_stream=files_stream)
                    reply = response.get("response", "No response from assistant")
                    shutil.rmtree(save_path_root, ignore_errors=True)
                    st.session_state.chat_history.append({
                        "user_input": input,
                        "assistant_reply": reply,
                        "sources": response.get("sources", ["no reply received"]),
                        "tools_used": response.get("tools_used", ["no tools were used"]),
                        "raw_contents": response.get("raw_contents", ["no raw contents retrieved"])
                    })
        
        clear_chat = st.button("Clear current chat", key="clear_current_chat_with_upload")
        chat_messages_container = st.container()
        if clear_chat:
            ImpaxAIRAAPI.clear_chat_session(st.session_state.session_id)
            st.session_state.chat_history.pop()
            del st.session_state.session_id
            st.info("Chat has been cleared.") 
            chat_messages_container.write("")
        # Display chat history in descending order
        with chat_messages_container:
            for i, chat_message in enumerate(reversed(st.session_state.chat_history)):
                col1, col2 = st.columns([2, 3]) 
                with col1:
                    st.markdown(f"### User message:\n{chat_message['user_input']}")
                    st.markdown(f"### Assistant reply:\n{chat_message['assistant_reply']}")
                    st.markdown("---")  # Optional: Adds a line for better separation
                with col2:
                    st.markdown("### Source:")
                    sources_df = pd.DataFrame(chat_message['sources'])
                    st.dataframe(sources_df)

                    st.markdown("------\n")
                    st.markdown("### Tools used by the assistant:")
                    st.markdown("- " + "- ".join([f"`{t.strip()}`\n" for t in chat_message.get("tools_used")]))

                    st.markdown("------\n")
                    st.markdown("### Show raw content:")
                    show_raw_content = st.button("Show raw content", key=f"show_raw_content_chat_with_upload_button_{i}")
                    hide_raw_content = st.button("Hide raw content", key=f"hide_raw_content_chat_with_upload_button_{i}")
                    raw_content_containers = []
                    raw_content_containers.append(st.empty())
                    if show_raw_content:
                        raw_content_containers[i].write("\n".join(chat_message.get("raw_contents")))
                    if hide_raw_content:
                        raw_content_containers[i].write("")
                st.divider()

def ten_step_writing():
    st.header("10 Step Writing")
    company_name = st.text_input("Enter the company name here")
    if st.button("Run", key="run_ten_step"):
        generator = ImpaxAIRAAPI.write_ten_steps(company_name)
        for item in generator:
            title, content = item
            display = f"## {title}\n{content}"
            st.markdown(display)
            st.divider()
        

def research_search():
    simple_search, search_in_steps = st.tabs(["Simple Search", "Complex Questions"])
    with simple_search:
        st.caption("Use this for simple questions. The assistant will automatically choose the most appropriate data source it has.")
        with st.form(key="simple_search_input"):
            input = st.text_area("Enter your questions here: ")
            submit_button = st.form_submit_button(label='Submit')
            if submit_button and input:
                results = ImpaxAIRAAPI.simple_search(input)
                response_text = results["response_text"]
                sources = results["metadatas"]
                sources_df = pd.DataFrame(sources)
                col1, col2 = st.columns([2, 3]) 
                with col1:
                    st.markdown("### Answer:\n" + response_text)
                with col2:
                    st.dataframe(sources_df)
    with search_in_steps:
        st.caption("Use this for the more complex questions, which may require the assistant to work in steps. "
                   "This will take longer than the simple search method. ")
        with st.form( key="multistep_search_input"):
            input = st.text_area("Enter your questions here: ")
            submit_button = st.form_submit_button(label='Submit')
            if submit_button and input:
                results = ImpaxAIRAAPI.multistep_search(input)
                response_text = results["response_text"]
                sources = results["metadatas"]
                sources_df = pd.DataFrame(sources)
                col1, col2 = st.columns([2, 3]) 
                with col1:
                    st.markdown("### Answer:\n" + response_text)
                with col2:
                    st.dataframe(sources_df)
# def data_ingestion():
#     st.header("Data Ingestion")
#     file_path = st.text_input("Enter file path")
#     data_format_list = ["CSV", "JSON", "Excel"]
#     selected_format = st.selectbox("Select data format", data_format_list)
#     if st.button("Run"):
#         # Implement your business logic for data ingestion here
#         st.write(f"Ingesting {selected_format} data from '{file_path}'...")

def main():
    st.title("Impax AI Investment Assistant Demo")
    st.caption("version: alpha 0.2.1")
    
    sections = SECTIONS
    selected_section = st.sidebar.radio("Select a section", sections)
    # authentication block
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state['logged_in']:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if utils.check_credentials(username, password):
                    st.session_state['logged_in'] = True
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Incorrect username or password")
    else:
        if selected_section == "Introduction":
            st.markdown("## Introduction\n"
                "There are 4 sections in this web app: \n"
                "### Impax Investment Assistant\n"
                "This section implements a chat-based investment assistant. \n"
                "This chat assistant comes in two modes: \n - You can either "
                "directly chat with it;'\n - or upload files and chat"
                " based on the files you upload.\n"
                "- We have connected the chat assistant "
                "to various internal and external resources. "
                "Try to be specific in your questions, "
                "such as include specific keywords, "
                "date ranges, and sectors in your questions.\n"
                
                "### Research Search\n"
                "- This is a faster method and only allows on-off questions. "
                "- Your questions here will be automatically routed to different data sources. \n"
                
                "### Ten-step writing\n"
                "- This is an experimental feature.\n"
                "- Our AI agent can look up in the annual reports, "
                "internet search, and internal research to write research "
                "documents autonomously.\n"

                "### Feedback\n"
                "(This is under construction. "
                "If you have any feedbacks, we are happy to hear about it."
                )
        if selected_section == "Impax Investment Assistant":
            chat_engine()
        elif selected_section == "Research Search":
            research_search()
        elif selected_section == "10 Step Writing":
            ten_step_writing()
        elif selected_section == "Feedback":
            st.write("Under construction.")
        elif selected_section == "Data Ingestion":
            raise NotImplementedError
            data_ingestion()

if __name__ == "__main__":

    main()