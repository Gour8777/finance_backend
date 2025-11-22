def build_prompt(intent, user_prompt, context, transactions, no_txn_message=None):
    prompt_parts = ["You are a helpful Indian financial assistant.\n"]

    # ----------------------------------------------------
    # 0️⃣ IF NO TRANSACTIONS IN THIS PERIOD
    # ----------------------------------------------------
    if intent in ["expense_query", "expense_analysis", "savings_advice"]:
        if no_txn_message:
            # Example: "No transactions found in the last 15 days"
            prompt_parts.append(
                f"User asked: {user_prompt}\n"
                f"{no_txn_message}.\n"
                f"Respond accordingly. Provide a general helpful financial response."
            )
            return "\n".join(prompt_parts)

    # ----------------------------------------------------
    # 1️⃣ BUDGET QUERY
    # ----------------------------------------------------
    if intent == "budget_query":
        spent = sum(t['amount'] for t in transactions)
        budget = context.get('budget', 0)
        balance = budget - spent
        prompt_parts.append(
            f"User's monthly budget is ₹{budget}, spent ₹{spent}, balance ₹{balance}.\n"
            "Provide a direct budget status update."
        )

    # ----------------------------------------------------
    # 2️⃣ EXPENSE QUERY
    # ----------------------------------------------------
    elif intent == "expense_query":
        txn_summary = "\n".join([f"- {t['category']}: ₹{t['amount']}" for t in transactions])
        prompt_parts.append(
            f"User asked about expenses.\n"
            f"Transactions:\n{txn_summary}\n"
            "Provide a clear expense summary."
        )

    # ----------------------------------------------------
    # 3️⃣ EXPENSE ANALYSIS
    # ----------------------------------------------------
    elif intent == "expense_analysis":
        txn_summary = "\n".join([f"- {t['category']}: ₹{t['amount']}" for t in transactions])
        prompt_parts.append(
            f"User wants expense analysis.\n"
            f"Transactions:\n{txn_summary}\n"
            "State the top spending category, amount, and percentage of total."
        )

    # ----------------------------------------------------
    # 4️⃣ INVESTMENT QUERY
    # ----------------------------------------------------
    elif intent == "investment_query":
        prompt_parts.append(
            f"User income: ₹{context.get('income')}, "
            f"risk: {context.get('risk_level')}, "
            f"goal: {context.get('goal')}.\n"
            "Provide practical investment recommendations."
        )

    # ----------------------------------------------------
    # 5️⃣ SAVINGS ADVICE
    # ----------------------------------------------------
    elif intent == "savings_advice":
        txn_summary = "\n".join([f"- {t['category']}: ₹{t['amount']}" for t in transactions])
        prompt_parts.append(
            f"User asked for savings advice.\n"
            f"Transactions:\n{txn_summary}\n"
            "Provide actionable, realistic savings tips."
        )

    # ----------------------------------------------------
    # 6️⃣ FOLLOW-UP
    # ----------------------------------------------------
    elif intent == "followup":
        prompt_parts.append(
            f"Follow-up query: {user_prompt}.\n"
            f"Previous bot response: {context.get('last_bot_response')}.\n"
            "Continue the conversation helpfully."
        )

    # ----------------------------------------------------
    # 7️⃣ DEFAULT
    # ----------------------------------------------------
    else:
        prompt_parts.append(
            f"User asked: {user_prompt}. "
            "Provide a helpful, direct response."
        )

    return "\n".join(prompt_parts)
