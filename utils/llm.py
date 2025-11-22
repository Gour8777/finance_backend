import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def ask_llm(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful finance assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
