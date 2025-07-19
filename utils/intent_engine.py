from sentence_transformers import SentenceTransformer, util

class IntentEngine:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight & fast
        self.intent_map = {
            "greeting": ["hi", "hello", "hey","hii","good morning", "good evening", "good night"],
            "acknowledgment": ["ok", "okay", "thanks", "thank you"],
            "budget_query": ["what's my budget", "budget status","how much can i spend", "budget left"],
            "expense_query": ["expenses", "how much did i spend"],
            "expense_analysis": ["where did i spend most", "top spending category", "spending analysis", "expense breakdown", "spending habits"],
            "investment_query": ["investments", "portfolio", "sip", "mutual fund","suggest me some good stocks","where to invest"],
            "savings_advice": ["how to save", "reduce spending", "save more", "cut costs", "save money", "savings tips", "financial advice"],
            "followup": ["tell me more", "and what about"," can you explain", "more details", "can you elaborate", "what else"],
        }
        self.threshold = 0.6  # Adjust based on testing for accuracy vs. generalization

    def detect_intent(self, user_input):
        input_emb = self.model.encode(user_input, convert_to_tensor=True)
        best_score = -1
        matched_intent = "unknown"

        for intent, samples in self.intent_map.items():
            sample_embs = self.model.encode(samples, convert_to_tensor=True)
            score = util.pytorch_cos_sim(input_emb, sample_embs).max().item()
            if score > best_score:
                best_score = score
                matched_intent = intent

        if best_score < self.threshold:
            matched_intent = "unknown"

        return matched_intent
