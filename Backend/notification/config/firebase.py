import os
import json

def initialize_firebase():
    cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    cred_path = os.getenv("FIREBASE_CREDENTIALS")

    if not cred_json and not cred_path:
        print("Firebase Admin not configured, skipping initialization.")
        return

    try:
        import firebase_admin
        from firebase_admin import credentials

        if firebase_admin._apps:
            return

        if cred_json:
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            print("Firebase Admin initialized from FIREBASE_CREDENTIALS_JSON")
        else:
            cred = credentials.Certificate(cred_path)
            print(f"Firebase Admin initialized from file: {cred_path}")

        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Error initializing Firebase Admin: {e}")
