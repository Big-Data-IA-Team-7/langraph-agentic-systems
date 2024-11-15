# langraph-agentic-systems

## Overview

A research tool designed for efficient document parsing, vector storage, and multi-agent research using **Airflow**, **Pinecone**, and **Langraph**. This end-to-end solution supports document analysis, interactive Q&A, and professional reporting. The project is powered by a user-friendly interface built with **Streamlit**, enabling streamlined research and interactive document exploration.

## Project Resources

## Project Resources

- **Google Codelab**: [Codelab Link](https://codelabs-preview.appspot.com/?file_id=1vszytuEvvTvKJ0HBTtyutGN9P6chE_JkjfU5P4c9TVY#0)
- **App (Deployed on AWS EC2)**: [Streamlit Link](http://75.101.133.31:8501/)
- **Airflow (Deployed on AWS EC2)**: [Airflow Link](http://75.101.133.31:8080/)
- **YouTube Demo**: [Demo Link](https://www.youtube.com/watch?v=rMcNf_Q8OeE)

## Features

### Document Parsing and Vector Storage

- **Docling Integration with Langchain**: Parses documents to extract structured information.
- **Vector Storage**: Stores document vectors in Pinecone for scalable and fast similarity searches.
- **Airflow Pipeline**: Automates the parsing and storage process, ensuring efficient data handling.

### Multi-Agent Research System (using LangGraph)

- **Document Selection**: Provides access to parsed documents for research purposes.
- **Arxiv Agent**: Retrieves relevant research papers.
- **Web Search Agent**: Expands the research context through online searches.
- **RAG Agent**: Answers user queries using Retrieval-Augmented Generation with Pinecone.

### User Interface and Interaction

- **Streamlit or Coagents**: Interactive platform for conducting research and asking questions (5-6 per document).
- **Session Saving**: Stores the results of each research session for future reference.
- **Professional PDF Export**: Generates templated reports summarizing research findings.
- **Codelabs Format**: Structures findings for instructional clarity and reuse.

## Architecture

The application includes the following main components:

1. **Document Parsing Pipeline**: Extracts structured information from the provided dataset using Docling with Langchain.
2. **Vector Storage**: Saves vectors in Pinecone for efficient document querying.
3. **Research Agents**: Utilizes Langraph to deploy multi-agent systems for comprehensive research.
4. **User Interface**: Built with Streamlit or Coagents for seamless user interaction.
5. **Report Generation**: Professional PDF export and Codelabs formatting for documentation.

## Technologies

- **Python**: Core programming language
- **Airflow**: Workflow orchestration and automation
- **Docling**: Document parsing and structuring
- **Pinecone**: Vector database for similarity search
- **Langraph**: Multi-agent system framework
- **Streamlit**: User interface development
- **Docker**: Containerization for deployment

## Architecture Diagram

Include diagrams here showcasing the Airflow pipeline, multi-agent research system, and user interface workflows.

#### Document Parsing and Vector Storage Architecture Diagram

<img width="721" alt="image" src="https://github.com/user-attachments/assets/e3534695-3590-41e4-82d1-344c14fbafb7">

#### Langgraph Design

<img width="669" alt="image" src="https://github.com/user-attachments/assets/105950e5-b62a-4632-bf6a-acf95abbd659">

#### Streamlit and FastAPI Architecture

<img width="652" alt="image" src="https://github.com/user-attachments/assets/5bad6f9c-adfc-48c0-9891-d16f775df843">

---

## Project References

- **Docling**: [GitHub Link](https://github.com/DS4SD/docling)
- **Pinecone**: [Official Website](https://www.pinecone.io/)
- **Langraph**: [Tutorial](https://langchain-ai.github.io/langgraph/tutorials/introduction/)

## How to Run the Application

### Prerequisites

- Pinecone API key
- SerpAPI Key
- Langsmith
- OpenAI API Key

### Clone the Repository

```bash
# Clone the repository

git clone https://github.com/Big-Data-IA-Team-7/langraph-agentic-systems
cd langraph-agentic-systems

# For Streamlit and FastAPI frontend
#Build the image
docker build -t fast-api-streamlit-1:latest .

# To run the image
docker run -d -p 8000:8000 -p 8501:8501 fast-api-streamlit-1


#To run Airflow pipeline

cd airflow

docker build -t airflow-pipeline-3 .
docker run -d -p 8080:8080 airflow-pipeline-3

```

## Contributions

| Name                         | Contribution                                                                                                                           |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Pragnesh Anekal              | 33% - Langcahin, building Graph using LangGraph, Airflow, Streamlit Front end, building the chat interface, Integrating Download files |
| Ram Kumar Ramasamy Pandiaraj | 33% - Web scraping, Snowflake setup, Docling, Airflow Pipeline, Fast API , Pinecone, Arxiv Agent                                       |
| Dipen Manoj Patel            | 33% - Streamlit Front end, Web Search using SerpAPI, Extract as PDF, Codelabs, Deploying Streamlit and FastAPI                         |

## Attestation

**WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK.**
