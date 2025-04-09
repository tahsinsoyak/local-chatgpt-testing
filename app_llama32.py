import chainlit as cl
import ollama

@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "interaction",
        [{"role": "system", "content": "You are a helpful assistant powered by Llama 3.2."}]
    )
    msg = cl.Message(content="")
    start_message = "Hi there! I'm Llama 3.2, a compact local model. Ask me anything (text-only)!"
    for token in start_message:
        await msg.stream_token(token)
    await msg.send()

@cl.step(type="tool")
async def tool(input_message: str):
    interaction = cl.user_session.get("interaction")
    interaction.append({"role": "user", "content": input_message})
    
    try:
        stream = ollama.chat(model="llama3.2", messages=interaction, stream=True)
        response_content = ""
        for chunk in stream:
            if "message" in chunk and "content" in chunk["message"]:
                response_content += chunk["message"]["content"]
                yield chunk["message"]["content"]
        interaction.append({"role": "assistant", "content": response_content})
    except Exception as e:
        error_msg = f"Error with Llama 3.2: {str(e)}"
        interaction.append({"role": "assistant", "content": error_msg})
        yield error_msg

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    async for token in tool(message.content):
        await msg.stream_token(token)
    await msg.send()

if __name__ == "__main__":
    import os
    os.system("chainlit run app_llama32.py -w")