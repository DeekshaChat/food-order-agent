import json
import ollama
from app import tools

MODEL = "qwen2.5:7b"
MAX_STEPS = 6  # stop runaway tool loops

SYSTEM_PROMPT = """You are a food ordering assistant for a delivery app. Prices are in Indian rupees (₹).

You MUST call a tool to answer any question about dishes, prices, availability, the cart or orders.
Never answer these from memory and never reply with a generic greeting when the user asks something specific.

Examples:
- "price of masala dosa" -> call search_menu with query "masala dosa"
- "show veg dishes under 150" -> call search_menu with veg_only true, max_price 150
- "add 2 of those" -> call add_to_cart with the item_id from the earlier search results
- "what's in my cart" -> call view_cart
- "where is my order" -> call get_order_history

Rules:
- Use item_id values exactly as returned by search_menu. Never guess an item_id.
- If the user mentions an allergy, use exclude_allergen when searching.
- Before calling place_order, show the cart and total and ask the user to confirm.
  Only call place_order after the user clearly says yes.
- If a tool returns an error, explain it simply and suggest what to do next.
- Keep replies short."""


# user_id is NOT in these schemas on purpose: the model must never choose it.
TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "search_menu",
        "description": "Search available dishes by keyword, max price, veg preference, or allergen to avoid.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "dish, cuisine or restaurant, e.g. 'pizza'"},
            "max_price": {"type": "number", "description": "maximum price in rupees"},
            "veg_only": {"type": "boolean", "description": "true for vegetarian only"},
            "exclude_allergen": {"type": "string", "description": "e.g. nuts, dairy, gluten, soy, egg"},
        }, "required": []}}},
    {"type": "function", "function": {
        "name": "add_to_cart",
        "description": "Add a menu item to the user's cart.",
        "parameters": {"type": "object", "properties": {
            "item_id": {"type": "integer", "description": "item_id from search_menu"},
            "quantity": {"type": "integer", "description": "1 to 10"},
        }, "required": ["item_id"]}}},
    {"type": "function", "function": {
        "name": "view_cart",
        "description": "Show the items and total in the user's cart.",
        "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {
        "name": "place_order",
        "description": "Place an order for the whole cart. Only call after the user confirms.",
        "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {
        "name": "get_order_status",
        "description": "Get the status of one order by its order_id.",
        "parameters": {"type": "object", "properties": {
            "order_id": {"type": "integer"},
        }, "required": ["order_id"]}}},
    {"type": "function", "function": {
        "name": "get_order_history",
        "description": "List the user's recent orders. Use when the user doesn't know the order id.",
        "parameters": {"type": "object", "properties": {}, "required": []}}},
]


TOOL_FUNCS = {
    "search_menu": tools.search_menu,
    "add_to_cart": tools.add_to_cart,
    "view_cart": tools.view_cart,
    "place_order": tools.place_order,
    "get_order_status": tools.get_order_status,
    "get_order_history": tools.get_order_history,
}

NEEDS_USER = {"add_to_cart", "view_cart", "place_order", "get_order_status", 
              "get_order_history"}


def run_tool(name, args, user_id):
    """Run one tool safely. Always returns a dict, never raises."""
    func = TOOL_FUNCS.get(name)
    if func is None:
        return {"error": f"Unknown tool '{name}'."}
    args = dict(args or {})
    args.pop("user_id", None)          # ignore anything the model tries to pass
    if name in NEEDS_USER:
        args["user_id"] = user_id      # the code decides who the user is
    try:
        return func(**args)
    except TypeError as e:
        return {"error": f"Bad arguments for {name}: {e}"}
    except Exception as e:
        return {"error": f"{name} failed: {e}"}



def chat(messages, user_id, verbose=True):
    """Run the agent loop for one user turn. `messages` is the running history."""
    nudged = False
    for step in range(MAX_STEPS):
        resp = ollama.chat(model=MODEL, messages=messages, tools=TOOL_SCHEMAS)
        msg = resp.message
        calls = msg.tool_calls or []
        if verbose:
            print(f"  [step {step}] tool_calls={len(calls)} content={msg.content!r}")

        if not calls:
            if (msg.content or "").strip():            # real final answer
                messages.append({"role": "assistant", "content": msg.content})
                return msg.content
            if not nudged:                              # empty reply: ask once more
                nudged = True
                messages.append({"role": "user", "content":
                    "Please answer my question in words, using the tool results above."})
                continue
            break

        # keep history as plain dicts
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [{"function": {"name": c.function.name,
                                         "arguments": dict(c.function.arguments)}}
                           for c in calls],
        })
        for call in calls:
            name, args = call.function.name, dict(call.function.arguments)
            result = run_tool(name, args, user_id)
            if verbose:
                print(f"  [tool] {name}({args}) -> {json.dumps(result)[:150]}")
            messages.append({"role": "tool", "tool_name": name,
                             "content": json.dumps(result)})

    return "Sorry, I couldn't complete that. Could you rephrase your request?"
