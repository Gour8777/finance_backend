import os
import json
import requests
import numpy as np
from typing import Dict, List
from dotenv import load_dotenv

# --- Load .env file ---
load_dotenv()

INTENT_MAP: Dict[str, List[str]] = {
    "greeting": [
        "hi", "hello", "hey", "hii", "yo", "good morning", 
        "good evening", "good night", "hey there", "hola"
    ],

    "acknowledgment": [
        "ok", "okay", "thanks", "thank you", "got it", 
        "sounds good", "great", "cool", "understood"
    ],

    "budget_query": [
        "what's my budget", "budget status", "how much can i spend",
        "budget left", "remaining budget", "tell me my budget",
        "current budget", "month budget", "budget details"
    ],

    "set_budget": [
        "set my budget", "i want to set a budget", 
        "update budget", "change my budget", 
        "set monthly budget", "create a budget"
    ],

    "expense_query": [
        "expenses", "how much did i spend", "show my spending",
        "my last transactions", "recent expenses", 
        "how much did i pay", "transaction history"
    ],

    "add_expense": [
        "add an expense", "record a spending", "note this expense",
        "log an expense", "i spent money", "save this expense"
    ],

    "expense_analysis": [
        "where did i spend most", "top spending category", 
        "spending analysis", "expense breakdown", 
        "spending habits", "biggest expense", 
        "category-wise spending", "monthly spending analysis"
    ],

    "investment_query": [
        "investments", "portfolio", "sip", "mutual fund",
        "suggest me some good stocks", "where to invest",
        "investment ideas", "best investment options",
        "stock suggestions", "investment plan"
    ],

    "investment_performance": [
        "investment returns", "portfolio performance",
        "how are my investments doing", "profit and loss in investments",
        "investment growth"
    ],

    "savings_advice": [
        "how to save", "reduce spending", "save more",
        "cut costs", "save money", "savings tips",
        "financial advice", "ways to save", 
        "how can i save money"
    ],

    "credit_card_query": [
        "recommended credit card", "best credit card",
        "which credit card should i get", "show me credit card options",
        "credit card suggestion", "card recommendation"
    ],

    "credit_card_benefits": [
        "card benefits", "what are the rewards", "reward points",
        "cashback details", "card features"
    ],

    "bill_query": [
        "upcoming bills", "pending bills", "show my bills",
        "when is my bill due", "bill reminders", "due payments"
    ],

    "followup": [
        "tell me more", "and what about", "can you explain",
        "more details", "can you elaborate", "what else", 
        "continue", "go on"
    ],

    "goodbye": [
        "bye", "goodbye", "see you", "talk to you later",
        "bye bye", "catch you later"
    ],

    "unknown": [
        "nonsense", "??", "what are you saying",
        "i don't know", "random", "confusing"
    ]
}

def embed_batch(texts: List[str]) -> List[List[float]]:
    account_id = os.getenv("CF_ACCOUNT_ID")
    api_key = os.getenv("CF_API_TOKEN")
    base_url = os.getenv("EMBED_BASE_URL") or f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run"
    model = os.getenv("EMBED_MODEL", "@cf/baai/bge-m3")

    if not account_id:
        raise RuntimeError("CF_ACCOUNT_ID missing in .env")
    if not api_key:
        raise RuntimeError("CF_API_TOKEN missing in .env")

    resp = requests.post(
        f"{base_url}/{model}",
        json={"text": texts},
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    vectors = None

    # 1) Workers AI common shape: {"result":{"data":[{"embedding":[...]}, ...]}}
    try:
        arr = data["result"]["data"]
        if isinstance(arr, list) and arr:
            if isinstance(arr[0], dict) and "embedding" in arr[0]:
                vectors = [item["embedding"] for item in arr]
            elif isinstance(arr[0], list):
                vectors = arr
    except Exception:
        pass

    # 2) OpenAI-style shape: {"data":[{"embedding":[...]}, ...]}
    if vectors is None:
        try:
            arr = data["data"]
            if isinstance(arr, list) and arr:
                if isinstance(arr[0], dict) and "embedding" in arr[0]:
                    vectors = [item["embedding"] for item in arr]
                elif isinstance(arr[0], list):
                    vectors = arr
        except Exception:
            pass

    # 3) Raw list fallback
    if vectors is None and isinstance(data, list) and data and isinstance(data[0], list):
        vectors = data

    if vectors is None:
        raise ValueError(f"Unexpected embeddings response shape: {data}")

    return vectors

    account_id = os.getenv("CF_ACCOUNT_ID")
    api_key = os.getenv("CF_API_TOKEN")
    base_url = os.getenv("EMBED_BASE_URL") or f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run"
    model = os.getenv("EMBED_MODEL", "@cf/baai/bge-m3")

    if not account_id:
        raise RuntimeError("CF_ACCOUNT_ID missing in .env")
    if not api_key:
        raise RuntimeError("CF_API_TOKEN missing in .env")

    resp = requests.post(
        f"{base_url}/{model}",
        json={"text": texts},
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    arr = data["result"]["data"]
    return [item["embedding"] for item in arr]


def main():
    out = {}
    for intent, samples in INTENT_MAP.items():
        print(f"Embedding → {intent} ({len(samples)} samples)")
        vecs = embed_batch(samples)
        out[intent] = vecs
        print(f"done {intent}: {len(vecs)}")

    with open("intent_embs.json", "w", encoding="utf-8") as f:
        json.dump(out, f)

    print("\n✔️ Completed!")
    print("✔️ Saved → intent_embs.json")
    print("✔️ You can now use it in IntentEngine.\n")


if __name__ == "__main__":
    main()
