import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_openai_response(messages: list[dict]) -> str:
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content
