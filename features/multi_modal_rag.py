import streamlit as st
import requests
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

@st.fragment
def download_fragment(file_content: bytes, file_name: str) -> None:
    st.download_button('**Download File**', file_content, file_name=file_name, key="download_file_button")

def multi_modal_rag():

    if 'data_frame' not in st.session_state:
        st.session_state.data_frame = None
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    if 'history' not in st.session_state:
        st.session_state.history = None
    if 'title' not in st.session_state:
        st.session_state.title = None
    if 'file_path' not in st.session_state:
        st.session_state.file_path = None

    st.title('Multi Modal RAG, Summary and Report Generation App')

    # Fetch data from FastAPI endpoint
    response = requests.get(f"{os.getenv("FAST_API_URL")}/data/get-data/")
    if response.status_code == 200:
        data = response.json()
        st.session_state.data_frame = pd.DataFrame(data)
        
        if not st.session_state.data_frame.empty:
            selected_title = st.selectbox("**Select a PDF Title**:", ["Select a title"] + st.session_state.data_frame['TITLE'].tolist())
            
            if selected_title != "Select a title":
                selected_row = st.session_state.data_frame[st.session_state.data_frame['TITLE'] == selected_title].iloc[0]

                st.session_state.title = selected_row['TITLE']
                # Create columns for layout
                image_col, title_col = st.columns([1, 3])

                # Display the image in the first column
                with image_col:
                    if selected_row['IMAGE_URL'] != '':
                        st.image(selected_row['IMAGE_URL'], width=150)
                    else:
                        st.text("No Image present")
                
                    pdf_url = selected_row['PDF_S3_URL']
                    st.session_state.file_name = pdf_url.split("/")[-1]
                    
                    response_pdf = requests.get(
                        f"{os.getenv("FAST_API_URL")}/data/extract-file/",
                        params={"file_name": st.session_state.file_name},
                        stream=True
                    )

                    if response_pdf.status_code == 200:
                        
                        download_fragment(response_pdf.content, st.session_state.file_name)

                    else:
                        st.error("Failed to download the PDF file.")
                # Display the title and summary in the second column
                with title_col:
                    st.subheader(selected_row['TITLE'])
                    st.write("**Summary**: ", selected_row['BRIEF_SUMMARY'])

                if st.button("**Chat With PDF**"):
                        st.session_state.chat_with_pdf = True
                        st.session_state.history = []
                        st.rerun()
        else:
            st.write("No data available.")
    elif response.status_code == 401:
        st.error("Unauthorized: Invalid data.")
    else:
        st.error(f"An error occurred: {response.status_code} - {response.text}")
