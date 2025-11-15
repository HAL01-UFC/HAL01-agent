def should_continue_chatbot(state: dict):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tool"
    else:
        return "end"
