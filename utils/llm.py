import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # Load environment variables from .env

api_key = os.getenv("TOGETHER_API_KEY")

client = OpenAI(api_key=api_key, base_url="https://api.together.xyz/v1")

def ask_mistral(prompt):
    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        messages=[
            {"role": "system", "content": "You are a helpful financial assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
