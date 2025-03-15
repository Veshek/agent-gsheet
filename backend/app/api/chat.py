from fastapi import APIRouter, Depends, HTTPException, WebSocket
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio

from app.db.database import get_db
from app.models.user import User
from app.agents.react_agent import LangGraphAgent 
from app.core.dependencies import get_current_user
from langgraph_sdk import get_client
from app.core.config import (LANGGRAPH_SERVER)
from langchain_core.messages import HumanMessage


router = APIRouter()
react_agent = LangGraphAgent()

async def stream_response(user_input: str):
    """Stream response from LangGraph agent."""
    # Replace this with the URL of your own deployed graph
    client = get_client(url=LANGGRAPH_SERVER)
    input_message = HumanMessage(content=user_input)
    thread = await client.threads.create()
    # Start conversation with the initial message
    async for event in client.runs.stream(thread["thread_id"], 
                                        assistant_id="agent", 
                                        input={"messages": [input_message]}, 
                                        stream_mode="messages-tuple"):
        if event.event == 'messages':
            yield event.data[0]["content"]

@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket):
    """WebSocket endpoint for users to interact with the LangGraph agent."""
    await websocket.accept()
    try:
        while True:
            # Receive a message from the WebSocket
            data = await websocket.receive_text()
            print(data)
            # Stream the response from the LangGraph agent
            async for response in stream_response(user_input=data):
                await websocket.send_text(response)  # Send each chunk back to the client
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()