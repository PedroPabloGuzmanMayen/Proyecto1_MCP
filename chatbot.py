import anthropic

client = anthropic.Anthropic()


while True:

    user_message = input("Ingresa tu mensaje: ")
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ]
    )
    print(message.content)