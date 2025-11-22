import os
import json
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from google.oauth2 import service_account
from google.cloud import firestore

from auth.verify import verify_id_token
from utils.intent_engine import IntentEngine
from utils.slot_extraction import extract_time_window
from utils.context_engine import ContextEngine
from utils.prompt_builder import build_prompt
from utils.llm import ask_llm


# --------------------
# Load env + Firestore
# --------------------
load_dotenv()

router = APIRouter()

# FIREBASE_CREDENTIALS should be a JSON string in .env
# Example:
# FIREBASE_CREDENTIALS={"type":"service_account", ...}
firebase_creds_str = os.getenv("FIREBASE_CREDENTIALS")
if not firebase_creds_str:
    raise RuntimeError("FIREBASE_CREDENTIALS missing in .env")

firebase_creds = json.loads(firebase_creds_str)
gcp_credentials = service_account.Credentials.from_service_account_info(firebase_creds)

db = firestore.Client(
    project=firebase_creds["project_id"],
    credentials=gcp_credentials
)

intent_engine = IntentEngine()
context_engine = ContextEngine(db)


class ChatbotRequest(BaseModel):
    prompt: str


@router.post("/chatbot")
async def chatbot(request: ChatbotRequest, authorization: str = Header(None)):
    user_prompt = (request.prompt or "").strip()
    if not user_prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token_id = authorization.split(" ")[1]
    uid = verify_id_token(token_id)

    # -------- 1) Detect intent --------
    intent = intent_engine.detect_intent(user_prompt)
    print(intent)
    

    # Followup -> reuse last intent
    if intent == "followup":
        last_intent = context_engine.get_user_context(uid, "last_intent")
        if last_intent:
            intent = last_intent
    if intent == "unknown":
        bot_response = (
            "I'm your personal financial adviser 🤝\n"
            "You can ask me things like:\n"
            "• 'Show my last 15 days expenses'\n"
            "• 'What is my budget left?'\n"
            "• 'Where did I spend most this month?'\n"
            "• 'Suggest some investments based on my risk level'\n"
            "Try asking in one of these ways."
        )
        context_engine.set_user_context(uid, "last_intent", intent)
        context_engine.set_user_context(uid, "last_bot_response", bot_response)

        return {"response": bot_response}

    # -------- 2) Fetch user profile --------
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()
    profile = user_doc.to_dict() if user_doc.exists else {}

    # -------- 3) Decide txn needs --------
    expense_only_intents = {"expense_query", "expense_analysis", "budget_query"}
    both_income_expense_intents = {"savings_advice"}

    needs_expense_only = intent in expense_only_intents
    needs_both = intent in both_income_expense_intents

    transactions = []
    no_txn_message = None  # important: defined for all paths

    if needs_expense_only or needs_both:
        # Extract window + detect if user EXPLICITLY asked for a window
        extracted_days = extract_time_window(user_prompt)  # should return None if not found
        explicit_window = extracted_days is not None
        days = extracted_days or 30

        cutoff_ts = datetime.now(timezone.utc) - timedelta(days=days)
        txn_ref = user_ref.collection("transactions")

        # ✅ INDEX-FREE primary fetch: only timestamp filter
        docs = txn_ref.where("timestamp", ">=", cutoff_ts).stream()

        for doc in docs:
            data = doc.to_dict() or {}
            ttype = data.get("type")

            # For expense-only intents, keep only expenses
            if needs_expense_only and ttype != "expense":
                continue

            transactions.append({
                "type": ttype,
                "category": data.get("category"),
                "amount": float(data.get("amount", 0) or 0),
                "timestamp": data.get("timestamp"),
            })

        # ✅ If user explicitly asked a window and nothing found -> NO fallback
        if explicit_window and not transactions:
            no_txn_message = f"No transactions found in the last {days} days."

        # ✅ Fallback ONLY if user did NOT ask a specific window
        elif not transactions:
            fallback_docs = (
                txn_ref.order_by("timestamp", direction=firestore.Query.DESCENDING)
                      .limit(100)
                      .stream()
            )
            for doc in fallback_docs:
                data = doc.to_dict() or {}
                ttype = data.get("type")

                if needs_expense_only and ttype != "expense":
                    continue

                transactions.append({
                    "type": ttype,
                    "category": data.get("category"),
                    "amount": float(data.get("amount", 0) or 0),
                    "timestamp": data.get("timestamp"),
                })

    # -------- 4) Derived totals ONLY from fetched window --------
    income_total = 0.0
    expense_total = 0.0
    for t in transactions:
        if t.get("type") == "income":
            income_total += t.get("amount", 0.0)
        elif t.get("type") == "expense":
            expense_total += t.get("amount", 0.0)

    context = {
        "budget": profile.get("budget"),
        "goal": profile.get("goal"),
        "risk_level": profile.get("risk_level"),
        "derived_income": income_total if income_total > 0 else None,
        "derived_expense": expense_total if expense_total > 0 else None,
        "last_bot_response": context_engine.get_user_context(uid, "last_bot_response"),
        "last_intent": context_engine.get_user_context(uid, "last_intent"),
    }

    # -------- 5) Build prompt + call LLM --------
    final_prompt = build_prompt(
        intent=intent,
        user_prompt=user_prompt,
        context=context,
        transactions=transactions,
        no_txn_message=no_txn_message
    )

    print(final_prompt)
    bot_response = ask_llm(final_prompt)

    # -------- 6) Update context memory --------
    context_engine.set_user_context(uid, "last_intent", intent)
    context_engine.set_user_context(uid, "last_bot_response", bot_response)

    return {"response": bot_response}
