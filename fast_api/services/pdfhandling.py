import re
import boto3
import base64
import pdfkit
import markdown
from config import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY
import os

# Initialize boto3 client for S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Function to get image as Base64 from S3
def get_image_base64_from_s3(s3_url):
    # Extract bucket and key from S3 URL
    s3_parts = s3_url.replace("s3://", "").split("/", 1)
    bucket_name = s3_parts[0]
    key = s3_parts[1]
    try:
        # Retrieve the image data from S3 as bytes
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=key)
        image_data = s3_object['Body'].read()

        # Encode image data to Base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        print(f"Image from {s3_url} successfully converted to Base64.")
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        print(f"Error retrieving image from S3: {e}")
        return None

# Function to convert specific markdown to PDF with Base64 images
def convert_markdown_to_pdf(md_text, output_pdf_file):
    # Define the pattern for matching S3 image URLs with potential placeholders in markdown
    s3_image_pattern = r"data:image/png;base64,Image Path:\s*(s3://[^\s)]+)"
    
    # Replace each S3 URL in markdown with its corresponding Base64 image data
    def replace_with_base64(match):
        s3_path = match.group(1)
        image_base64 = get_image_base64_from_s3(s3_path)
        return image_base64 if image_base64 else s3_path  # Fall back to original S3 path if conversion fails

    # Perform the replacement
    md_text = re.sub(s3_image_pattern, replace_with_base64, md_text)
    # # Configure PDF options, if necessary
    # pdf_options = {
    #     'quiet': '',
    #     'enable-local-file-access': None,  # required for base64 images
    # }

    html_content = markdown.markdown(md_text)

    # Use pdfkit to convert the HTML to PDF
    try:
        pdfkit.from_string(html_content, output_pdf_file)
        print(f"PDF successfully generated: {output_pdf_file}")
    except Exception as e:
        print(f"Error generating PDF: {e}")