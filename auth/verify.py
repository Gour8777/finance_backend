import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

def verify_id_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        return uid
    except Exception as e:
        raise Exception("Invalid or expired token")
