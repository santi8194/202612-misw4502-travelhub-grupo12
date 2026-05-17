import os
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    if not firebase_admin._apps:
        # Default path, you can set FIREBASE_CREDENTIALS in .env
        cred_path = os.getenv("FIREBASE_CREDENTIALS", "travel-hub-grupo-12-firebase-adminsdk-fbsvc-b1556bcab2.json")
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin initialized successfully")
        except Exception as e:
            print(f"Error initializing Firebase Admin: {e}")
