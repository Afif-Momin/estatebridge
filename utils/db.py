import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("config.json")  # Your Firebase service account key
firebase_admin.initialize_app(cred)
db = firestore.client()

