import os, json, requests, numpy as np
from functools import lru_cache
from typing import List, Dict

class IntentEngine:
    def __init__(self, emb_path: str = "utils/intent_embs.json"):
        # same intent map (for reference / future edits)
        self.intent_map: Dict[str, List[str]] = {
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
        self.threshold: float = 0.6

        # --- Cloudflare env config ---
        self.account_id = os.environ.get("CF_ACCOUNT_ID", "")
        default_base = (
            f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run"
            if self.account_id else ""
        )
        self.base_url = os.environ.get("EMBED_BASE_URL", default_base)
        self.model = os.environ.get("EMBED_MODEL", "@cf/baai/bge-m3")
        self.api_key = os.environ.get("CF_API_TOKEN")

        if not self.api_key:
            raise RuntimeError("CF_API_TOKEN is not set")
        if not self.base_url:
            raise RuntimeError("EMBED_BASE_URL is not set (or CF_ACCOUNT_ID missing)")

        # --- load precomputed exemplar embeddings ---
        if not os.path.exists(emb_path):
            raise RuntimeError(
                f"{emb_path} not found. Run precompute_intents.py locally and commit the file."
            )

        with open(emb_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # convert to numpy arrays
        self.intent_embs: Dict[str, List[np.ndarray]] = {
            intent: [np.asarray(v, dtype=np.float32) for v in vec_list]
            for intent, vec_list in raw.items()
        }

    # ---------------------------
    # Embedding via CF (ONLY for user text now)
    # ---------------------------
    def _embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        if not texts:
            return []

        resp = requests.post(
            f"{self.base_url}/{self.model}",
            json={"text": texts},
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        # Workers AI common shape
        try:
            arr = data["result"]["data"]
            return [
                np.asarray(item["embedding"] if isinstance(item, dict) else item, dtype=np.float32)
                for item in arr
            ]
        except Exception:
            raise ValueError(f"Unexpected embeddings response shape: {data}")

    @lru_cache(maxsize=512)
    def _embed_text(self, text: str) -> np.ndarray:
        return self._embed_batch([text])[0]

    @staticmethod
    def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return float(np.dot(a, b) / (na * nb))

    def detect_intent(self, user_input: str) -> str:
        input_emb = self._embed_text(user_input)
        best_score = -1.0
        matched_intent = "unknown"

        for intent, sample_embs in self.intent_embs.items():
            if not sample_embs:
                continue
            score = max((self._cosine_sim(input_emb, e) for e in sample_embs), default=-1.0)
            if score > best_score:
                best_score = score
                matched_intent = intent

        if best_score < self.threshold:
            matched_intent = "unknown"

        print(matched_intent)
        return matched_intent
