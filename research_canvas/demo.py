"""Demo"""

import os
from dotenv import load_dotenv 
load_dotenv()

# pylint: disable=wrong-import-position
from fastapi import FastAPI
import uvicorn
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitSDK, LangGraphAgent
from copilotkit.langchain import copilotkit_messages_to_langchain
from agent import runnable

app = FastAPI()
sdk = CopilotKitSDK(
    agents=[
        LangGraphAgent(
            name="research_agent",
            description="Research agent.",
            agent=runnable,
        ),
    ],
)

add_fastapi_endpoint(app, sdk, "/copilotkit")

def main():
    """Run the uvicorn server."""
    port = 8000
    uvicorn.run("demo:app", host="127.0.0.1", port=port)
