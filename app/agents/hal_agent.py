from abc import ABC, abstractmethod
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph
import json
from datetime import datetime
import asyncio

from app.agents import state
from app.agents.prompts.agent_prompt import agent_prompt
from app.agents.state import AgentState
from app.utils.edge_conditions import should_continue_chatbot



class HALAgent(ABC):
    def __init__(self):
        self.llm = ChatOllama(model="qwen3:0.6b", temperature=0, max_tokens=600)
        self.base_tools = []
        self.agent_prompt = agent_prompt
        
    async def call_chatbot(self, state, config):
        if not all(tool in state["tools"] for tool in self.base_tools):
            state["tools"].extend(self.base_tools)
        last_message = state["messages"][-1] if state["messages"] else None
        agent_model = self.llm.bind_tools(state["tools"])
        
        prompt = self.agent_prompt
        replacements = {
            "{CURRENT_DATETIME}": str(datetime.now())
        }
        
        for placeholder, value in replacements.items():
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value or ""))

        if isinstance(last_message, ToolMessage) and hasattr(last_message, "direct_return") and last_message.direct_return:
            response = last_message.content
            aiMessage = AIMessage(
                content=response,
                direct_return=True)
            state["messages"].append(aiMessage)
            return {"messages": [aiMessage]}
        
        messages = [SystemMessage(content=prompt)] + state["messages"]
        response = await agent_model.ainvoke(messages, config)
        return {"messages": [response]}

    async def execute_tools(self, state):
        """Execute the tools for the agent"""
        outputs = []
        last_message = state["messages"][-1]

        if hasattr(last_message, 'processed') and last_message.processed:
            return {"messages": []}

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tools = state["tools"]
            tools_by_name = {tool.name: tool for tool in tools}
            tool = tools_by_name[tool_name]           

            try:
                tool_result = await tool.ainvoke(tool_args)
        
                if getattr(tool, "return_direct", False):
                    simulated_message = ToolMessage(
                        content=json.dumps(tool_result),
                        name=tool_name,
                        direct_return=True,
                        tool_call_id=tool_call["id"],
                    )
                    state["messages"].append(simulated_message)
                    last_message.processed = True
                    return {"messages": [simulated_message]}

                outputs.append(
                    ToolMessage(
                        content=json.dumps(tool_result),
                        name=tool_name,
                        tool_call_id=tool_call["id"],
                    )
                )

            except Exception as e:
                error_message = f"Error executing tool '{tool_name}': {str(e)}"
                outputs.append(
                    ToolMessage(
                        content=json.dumps({"error": error_message}),
                        name=tool_name,
                        tool_call_id=tool_call["id"],
                    )
                )
        last_message.processed = True
        return {"messages": outputs}

    async def create_graph(self):
        graph_builder = StateGraph(AgentState)
        
        graph_builder.add_node("chatbot", self.call_chatbot)
        graph_builder.add_node("agent_tools", self.execute_tools)

     
        chatbot_mapping = {
            "tool": "agent_tools", 
            "end": END,
        }
        
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("agent_tools", "chatbot")
        graph_builder.add_conditional_edges("chatbot", should_continue_chatbot, chatbot_mapping)

        return graph_builder.compile()
