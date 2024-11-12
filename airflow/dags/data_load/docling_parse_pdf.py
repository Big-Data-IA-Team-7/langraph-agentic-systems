import boto3
from typing import Iterator
from docling.document_converter import DocumentConverter
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from docling_core.types.doc import PictureItem
import os
import time
from docling_core.types.doc import ImageRefMode
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from dotenv import load_dotenv
from openai import OpenAI
import re
import base64

# Load environment variables
load_dotenv()

# Function to encode the image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# Function to describe the image using OpenAI API
def describe_image(image_path):
    base64_image = encode_image(image_path)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe what you see in this image."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )
    content = response.choices[0].message.content
    return content


# Function to upload a local file to S3
def upload_to_s3(local_file_path: str, s3_key: str):
    s3 = boto3.client('s3', aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
    with open(local_file_path, 'rb') as image_file:
        s3.put_object(Bucket=os.getenv("S3_BUCKET_NAME_4"), Key=s3_key, Body=image_file, ContentType='image/png')
    print(f"Uploaded image to {s3_key}")


# Process PDFs from S3 and store images locally, then upload to S3
def process_and_store_pdfs_from_s3():
    # Get AWS credentials and bucket info from environment variables
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket_name = os.getenv("S3_BUCKET_NAME_4")
    prefix = "research-files/"

    # Initialize OpenAI embeddings and Pinecone
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=os.getenv("OPENAI_API_KEY"))
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=pinecone_api_key)

    # Connect to S3 and list all PDF files in the bucket
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    pdf_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.pdf')]

    # Custom loader to load PDF files from S3
    class DoclingPDFLoader(BaseLoader):
        def __init__(self, file_paths: list[str]) -> None:
            IMAGE_RESOLUTION_SCALE = 2.0
            pipeline_options = PdfPipelineOptions()
            pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
            pipeline_options.generate_picture_images = True
            self._file_paths = file_paths
            self._converter = DocumentConverter(format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            })

        def lazy_load(self) -> Iterator[LCDocument]:
            for file_path in self._file_paths:
                # Download file from S3
                local_file = '/tmp/' + os.path.basename(file_path)
                s3.download_file(bucket_name, file_path, local_file)

                # Convert and yield as a document
                dl_doc = self._converter.convert(local_file).document
                text = dl_doc.export_to_markdown(image_mode=ImageRefMode.EMBEDDED)

                # Process each element in the document
                picture_counter = 0
                for element, _level in dl_doc.iterate_items():
                    if isinstance(element, PictureItem) and element.image:  # Check if picture image exists
                        picture_counter += 1
                        image_file_path = f"/tmp/{os.path.basename(file_path).split('.')[0]}-picture-{picture_counter}.png"
                        element.image.pil_image.save(image_file_path, "PNG")  # Save locally

                        # Generate description of the image
                        content = describe_image(image_file_path)
                        print(content)

                        base64image = encode_image(image_file_path)



                        # Create an S3 key and upload the image
                        image_key = f"images/{os.path.basename(file_path).split('.')[0]}/picture-{picture_counter}.png"
                        upload_to_s3(image_file_path, image_key)

                        # Return the image URL for later use
                        s3_url = f"s3://{bucket_name}/{image_key}"
                        print(f"Image uploaded to: {s3_url}")
                    

                        # Create the replacement text to replace the image element
                        doc_content_with_image = f"Image Path: {s3_url} - Image Description: {content} Image Description Ends"
                        print(doc_content_with_image)

                        # Replace the image reference with the new text (image URL and description)
                        text = text.replace(base64image, doc_content_with_image)

                        # Remove the local file after uploading
                        os.remove(image_file_path)

                # Yield the modified document with updated content
                yield LCDocument(page_content=text)

    # Process each file individually and create a Pinecone index for each
    for file_key in pdf_files:
        file_name = os.path.basename(file_key)
        index_name = re.sub(r'[^a-zA-Z0-9_-]', '_', file_name.split('.')[0])  # Clean index name

        # Check if the index already exists
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        if index_name not in existing_indexes:
            pc.create_index(
                name=index_name,
                dimension=3072,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            while not pc.describe_index(index_name).status["ready"]:
                time.sleep(1)

        index = pc.Index(index_name)

        # Load and process the document
        loader = DoclingPDFLoader(file_paths=[file_key])
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = loader.load()
        print(docs)
        splits = text_splitter.split_documents(docs)

        # Store processed documents in Pinecone (commented out to avoid unnecessary calls)
        vectorstore_from_docs = PineconeVectorStore.from_documents(
            splits,
            index_name=index_name,
            embedding=embeddings,
            pinecone_api_key=pinecone_api_key
        )
        print(f"Successfully processed and stored {len(splits)} document chunks into Pinecone index '{index_name}'")
