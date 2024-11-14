from fastapi import APIRouter, HTTPException, status
from fast_api.langgraph_api.agent import runnable
from fastapi.responses import StreamingResponse
import pandas
import List
import logging
from fast_api.langgraph_api.utilities import build_report



router = APIRouter()

@router.get("/get-langraph-response/")
def get_response(input_query: str):
    try:
        # Generate the file stream and metadata
        input = input_query
        chat_history = []
        
        out = runnable.invoke({
                 "input": input,
                "chat_history": chat_history,
        })

        return build_report(
            output=out["intermediate_steps"][-1].tool_input
        )
    
    except Exception as e:
        logging.error("Exception:", e)
        raise HTTPException(status_code=500, detail=f"Error fetching response from Langgraph: {str(e)}")