def build_prompt(intent, user_prompt, context, transactions=[]):
    prompt_parts = ["You are a helpful Indian financial assistant.\n"]

    if intent == "budget_query":
        spent = sum(t['amount'] for t in transactions)
        budget = context.get('budget', 0)
        balance = budget - spent
        prompt_parts.append(f"User's monthly budget is ₹{budget}, spent ₹{spent}, balance ₹{balance}.\nProvide a direct budget status update.")

    elif intent == "expense_query":
        txn_summary = "\n".join([f"- {t['category']}: ₹{t['amount']}" for t in transactions])
        prompt_parts.append(f"User asked about expenses.\nTransactions:\n{txn_summary}\nProvide a clear expense summary.")

    elif intent == "expense_analysis":
        txn_summary = "\n".join([f"- {t['category']}: ₹{t['amount']}" for t in transactions])
        prompt_parts.append(f"User wants expense analysis.\nTransactions:\n{txn_summary}\nState the top spending category, amount, and % of total.")

    elif intent == "investment_query":
        prompt_parts.append(
            f"User income: ₹{context.get('income')}, risk: {context.get('risk_level')}, goal: {context.get('goal')}.\nProvide practical investment recommendations."
        )

    elif intent == "savings_advice":
        txn_summary = "\n".join([f"- {t['category']}: ₹{t['amount']}" for t in transactions])
        prompt_parts.append(f"User asked for savings advice.\nTransactions:\n{txn_summary}\nProvide actionable savings tips.")

    elif intent == "followup":
        prompt_parts.append(f"Follow-up query: {user_prompt}.\nPrevious bot response: {context.get('last_bot_response')}.\nContinue the conversation helpfully.")
        print(prompt_parts)

    else:
        prompt_parts.append(f"User asked: {user_prompt}. Provide a helpful, direct response.")

    return "\n".join(prompt_parts)
