class ContextEngine:
    def __init__(self, db):
        self.db = db

    def set_user_context(self, uid, key, value):
        user_ref = self.db.collection("users").document(uid)
        user_ref.set({"context": {key: value}}, merge=True)

    def get_user_context(self, uid, key, default=None):
        user_ref = self.db.collection("users").document(uid)
        doc = user_ref.get()
        if doc.exists:
            context = doc.to_dict().get("context", {})
            return context.get(key, default)
        return default

    def clear_context(self, uid):
        user_ref = self.db.collection("users").document(uid)
        user_ref.update({"context": {}})
