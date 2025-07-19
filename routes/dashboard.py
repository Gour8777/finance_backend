from fastapi import APIRouter, Header, HTTPException
from auth.verify import verify_id_token

router = APIRouter()

@router.get("/dashboard")
async def dashboard(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    id_token = authorization.split(" ")[1]
    
    try:
        uid = verify_id_token(id_token)
        return {"message": f"Welcome user {uid} to your dashboard"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
