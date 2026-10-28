import ollama
from app.agent import SYSTEM_PROMPT, TOOL_SCHEMAS

MODELS = ["qwen2.5:7b", "qwen2.5:14b", "llama3.1:8b"]

# (user message, tool the model should call)
CASES = [
    ("price of rasmalai", "search_menu"),
    ("list products under 150", "search_menu"),
    ("price range less than 150", "search_menu"),
    ("what is the price of masala dosa", "search_menu"),
    ("show me veg pizza", "search_menu"),
    ("biryani without nuts", "search_menu"),
    ("add 2 of item 12 to my cart", "add_to_cart"),
    ("what's in my cart", "view_cart"),
    ("where is my order", "get_order_history"),
    ("status of order 3", "get_order_status"),
]

for model in MODELS:
    try:
        ok = 0
        print(f"\n=== {model} ===")
        for text, expected in CASES:
            msgs = [{"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text}]
            r = ollama.chat(model=model, messages=msgs, tools=TOOL_SCHEMAS)
            got = [c.function.name for c in (r.message.tool_calls or [])]
            hit = expected in got
            ok += hit
            print(f"{'PASS' if hit else 'FAIL'}  {text!r:<40} -> {got or r.message.content[:50]!r}")
        print(f"Score: {ok}/{len(CASES)}")
    except Exception as e:
        print(f"{model}: skipped ({e}). Run: ollama pull {model}")