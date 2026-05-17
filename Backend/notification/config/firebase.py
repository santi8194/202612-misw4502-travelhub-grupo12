import os
import json
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    if not firebase_admin._apps:
        # Try to load from environment variable first
        cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        cred_path = os.getenv("FIREBASE_CREDENTIALS", "travel-hub-grupo-12-firebase-adminsdk-fbsvc-b1556bcab2.json")
        
        try:
            if cred_json:
                # Initialize using the JSON string from environment variable
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
                print("Firebase Admin initialized from FIREBASE_CREDENTIALS_JSON")
            else:
                # Fallback to local JSON file
                cred = credentials.Certificate(cred_path)
                print(f"Firebase Admin initialized from file: {cred_path}")
                
            firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"Error initializing Firebase Admin: {e}")
