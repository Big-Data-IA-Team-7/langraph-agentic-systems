import streamlit as st
import requests
import os

def chat_pdf():
    st.title(f"Chat with {st.session_state.title}")
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'user_input' not in st.session_state:
        st.session_state.user_input = None
    if 'response' not in st.session_state:
        st.session_state.response = None

    user_input = st.chat_input("Enter your query:")

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state['history']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if user_input:
        st.session_state.user_input = user_input
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state['history'].append({"role": "user", "content": user_input})
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            params = {
                "file_name": st.session_state.file_name,
                "user_question": user_input
            }
            response = requests.get(
                f"{os.getenv("FAST_API_URL")}/query/ask-question/",
                params=params
            )

            if response.status_code == 200:
                # Parse the JSON response
                response_data = response.json()

                st.session_state.response = response_data
            
                message_placeholder.markdown(response_data)
                st.session_state['history'].append({"role": "assistant", "content": response_data})

    # Add a clear button
    if st.button("Clear Chat"):
        st.session_state['history'] = []
        st.rerun()