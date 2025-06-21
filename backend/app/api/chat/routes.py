from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.core.ai.service import get_answer_from_llm, get_answer_streaming
import logging
import json
from typing import AsyncGenerator

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    question: str
    thread_id: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint to get an answer from the LLM based on the user's question and thread ID.
    """
    try:
        logger.info(f"Received question: {request.question} for thread ID: {request.thread_id}")
        if not request.question or not request.thread_id:
            raise HTTPException(status_code=400, detail="Question and thread ID are required.")
        


        answer = await get_answer_from_llm(request.question, request.thread_id)
        logger.info(f"Got result: {answer}")

        if not isinstance(answer, dict) or "output" not in answer:
            raise ValueError("Invalid response format from get_answer")

        return ChatResponse(answer=answer["output"])
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
async def event_stream(question: str, thread_id: str) -> AsyncGenerator[str, None]:
    """
    Generator function to stream events.
    """
    try:
        async for chunk in get_answer_streaming(question, thread_id):
            if chunk:
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in event stream: {e}")
        yield json.dumps({"error": "Internal Server Error"})

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """
    Endpoint to get a streaming answer from the LLM based on the user's question and thread ID.
    """
    try:
        logger.info(f"Received question: {request.question} for thread ID: {request.thread_id}")
        if not request.question or not request.thread_id:
            raise HTTPException(status_code=400, detail="Question and thread ID are required.")

        return StreamingResponse(
            event_stream(request.question, request.thread_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Error in chat stream endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")