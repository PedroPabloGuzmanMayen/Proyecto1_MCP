import anthropic

client = anthropic.Anthropic()
conversation = []

while True:

    user_message = input("Ingresa tu mensaje: ")
    conversation.append({"role": "user", "content": user_message})
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages= conversation
    )

    reply = message.content[0].text
    print(reply)
    
    conversation.append({"role": "assistant", "content": reply})