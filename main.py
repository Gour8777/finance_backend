from fastapi import FastAPI
from routes import dashboard
from routes.profile import router as profile_router
from routes.user import router as user_router
from routes.chatbot import router as chatbot_router
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Finance backend working!"}

# Include routes
app.include_router(dashboard.router)
app.include_router(profile_router)
app.include_router(user_router)
app.include_router(chatbot_router)