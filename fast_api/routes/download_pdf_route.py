from fastapi import APIRouter, HTTPException, status
from fast_api.services.pdfhandling import convert_markdown_to_pdf
from fastapi.responses import StreamingResponse
import pandas as pd
import logging

router = APIRouter()

@router.get("/download-pdf/", response_model=List[dict])
def convert_to_pdf(md_text):
    try:
        # Generate the file stream and metadata
        md_text = md_text
        output_pdf_file = 'report_generated.pdf'

        convert_markdown_to_pdf(md_text,output_pdf_file)
    
    except Exception as e:
        logging.error("Exception:", e)
        raise HTTPException(status_code=500, detail=f"Error downloading the pdf: {str(e)}")
    