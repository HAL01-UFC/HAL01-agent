from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
import asyncio
import sys
from langchain_core.messages import HumanMessage
from app.agents.hal_agent import HALAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)

async def chat_with_agent_cli():
    agent = HALAgent()
    graph = await agent.create_graph()
    
    while True:
        try:
            user_input = input("you: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'sair']:
                break
            if not user_input:
                continue
            
            state = {
                "messages": [HumanMessage(content=user_input)],
                "tools": []
            }
            output = await graph.ainvoke(state)
            response = output["messages"][-1].content
            
            print(f"🤖 HAL-01: {response}")
            
        except KeyboardInterrupt:
            print("\n🤖 bye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(chat_with_agent_cli())
