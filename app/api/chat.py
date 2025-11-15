import base64
from fastapi.logger import logger
from fastapi import  File, Form, HTTPException, Response, UploadFile, APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse
import warnings
from fastapi import FastAPI

from app.services.chat_service import generate_chat_response

warnings.filterwarnings("ignore")

router = APIRouter()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@router.post("/api/agent")
async def get_chat_response(
    message_data: str,
):
    try:
        response = await generate_chat_response(message_data)

        return {"status": "success", "response": response }

    except HTTPException as e:
        logger.error(
            f"HTTP error during REST request: {str(e.detail)}"
        )
        raise e

    except Exception as e:
        logger.error(f"Error during REST request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

