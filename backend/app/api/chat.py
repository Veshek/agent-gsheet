from fastapi import APIRouter, Depends, HTTPException, WebSocket
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio

from app.db.database import get_db
from app.models.user import User
from app.agents.react_agent import LangGraphAgent 
from app.core.dependencies import get_current_user
from langchain_core.messages import HumanMessage

router = APIRouter()
react_agent = LangGraphAgent()

async def stream_response(user, user_input: str):
    """Stream response from LangGraph agent."""
    # get a corresponding thread id 
    # create new thread id if not provided
    #usercreate new thread 
    config = {"configurable": {"thread_id": "1"}}
    # Start conversation with the initial message
    for chunk in react_agent.agent.stream({"messages": [HumanMessage(content=user_input)]}, config, stream_mode="updates"):
        yield f"{chunk}|"

@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket, user: User = Depends(get_current_user)):
    """WebSocket endpoint for users to interact with the LangGraph agent."""
    await websocket.accept()
    try:
        while True:
            # Receive a message from the WebSocket
            data = await websocket.receive_text()
            # Stream the response from the LangGraph agent
            async for response in stream_response(user, data):
                await websocket.send_text(response)  # Send each chunk back to the client
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()