from app.agent import SYSTEM_PROMPT, chat

USER_ID = 1  # Asha, from the seed data

def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Food ordering agent (type 'quit' to exit)")
    while True:
        text = input("\nYou: ").strip()
        if text.lower() in {"quit", "exit"}:
            break
        if not text:
            continue
        messages.append({"role": "user", "content": text})   # this line was missing
        print(f"Agent: {chat(messages, USER_ID)}")

if __name__ == "__main__":
    main()