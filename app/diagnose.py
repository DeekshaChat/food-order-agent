import ollama
from app.agent import SYSTEM_PROMPT, TOOL_SCHEMAS, MODEL

QUESTION = "what is the price of masala dosa"
SEARCH_ONLY = [t for t in TOOL_SCHEMAS if t["function"]["name"] == "search_menu"]
WITH_PARAMS = [t for t in TOOL_SCHEMAS if t["function"]["parameters"]["properties"]]

def trial(label, tools, system, options=None):
    msgs = ([{"role": "system", "content": system}] if system else [])
    msgs.append({"role": "user", "content": QUESTION})
    r = ollama.chat(model=MODEL, messages=msgs, tools=tools, options=options or {})
    calls = [(c.function.name, dict(c.function.arguments)) for c in (r.message.tool_calls or [])]
    print(f"{label:<42} calls={calls} content={r.message.content!r}")

trial("1. all tools, no system prompt", TOOL_SCHEMAS, None)
trial("2. all tools + system prompt", TOOL_SCHEMAS, SYSTEM_PROMPT)
trial("3. all tools + system, temperature 0", TOOL_SCHEMAS, SYSTEM_PROMPT, {"temperature": 0})
trial("4. search_menu only + system prompt", SEARCH_ONLY, SYSTEM_PROMPT)
trial("5. tools with params only + system", WITH_PARAMS, SYSTEM_PROMPT)
trial("6. all tools + short system prompt", TOOL_SCHEMAS, "You are a food ordering assistant. Use tools to answer.")