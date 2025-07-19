from openai import OpenAI

client = OpenAI(api_key="7d6f9aa8a6b640fb68d97f80cc6014dd0ab1670f5c8a214181ab5252c6e47274", base_url="https://api.together.xyz/v1")

def ask_mistral(prompt):
    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        messages=[
            {"role": "system", "content": "You are a helpful financial assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
