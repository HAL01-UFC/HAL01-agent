import logging
import os
import re
import tempfile
import asyncio
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from langchain_core.messages import AIMessage, HumanMessage
from app.agents.hal_agent import HALAgent
from app.agents.state import AgentState

gunicorn_logger = logging.getLogger("gunicorn.error")


async def generate_chat_response(message_data: str):
    try:
        user_message = message_data.strip()
        state = {
            "messages":[HumanMessage(content=user_message)],
            "tools": []
        }
        agent = HALAgent()
        graph = await agent.create_graph()

        output = await graph.ainvoke(input=state)
        response = output["messages"][-1].content
        return response

    except Exception as e:
        error_message = f"Error processing message: {str(e)}"
        gunicorn_logger.error(error_message, exc_info=True)
        raise HTTPException(status_code=500, detail=error_message)

