from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from data_load.docling_parse_pdf import process_and_store_pdfs_from_s3


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}


# Define the DAG
with DAG(
    'langchain_rag',
    default_args=default_args,
    description='A DAG to parse pdfs and build Pinecone vector indexes',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    # Task 1: Scrape data
    parse_pdf_rag = PythonOperator(
        task_id='parse_pdf_rag',
        python_callable=process_and_store_pdfs_from_s3
    )

    parse_pdf_rag