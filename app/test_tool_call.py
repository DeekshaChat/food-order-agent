import ollama

tools = [{
    "type": "function",
    "function": {
        "name": "search_menu",
        "description": "Search food items on the menu",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "dish or cuisine"},
                "max_price": {"type": "number", "description": "max price in rupees"},
            },
            "required": ["query"],
        },
    },
}]

resp = ollama.chat(
    model="qwen2.5:7b",
    messages=[{"role": "user", "content": "Show me veg pizza under 300 rupees"}],
    tools=tools,
)
print(resp.message.tool_calls)