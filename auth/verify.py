import os
import json
from dotenv import load_dotenv
load_dotenv()
# ---------------------------
# 1. LOAD SERVICE ACCOUNT JSON
# ---------------------------
firebase_creds = json.loads(os.environ["FIREBASE_CREDENTIALS"])

# ---------------------------
# 2. INITIALIZE FIRESTORE CLIENT
# ---------------------------
from google.oauth2 import service_account
from google.cloud import firestore

gcp_credentials = service_account.Credentials.from_service_account_info(firebase_creds)
db = firestore.Client(
    project=firebase_creds["project_id"],
    credentials=gcp_credentials
)

# ---------------------------
# 3. INITIALIZE FIREBASE ADMIN AUTH
# ---------------------------
import firebase_admin
from firebase_admin import credentials as fb_credentials
from firebase_admin import auth

cred = fb_credentials.Certificate(firebase_creds)

# Prevent “App already exists” error in reload
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# ---------------------------
# 4. VERIFY TOKEN FUNCTION
# ---------------------------
def verify_id_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token["uid"]
    except Exception:
        raise Exception("Invalid or expired token")
