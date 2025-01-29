from fastapi import APIRouter, HTTPException, status, UploadFile, File
import os
import json
import firebase_admin
from firebase_admin import credentials, storage
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()  # Make sure you have .env to load the environment variables

# Load Firebase credentials from the environment variable
firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
if firebase_credentials_json is None:
    raise ValueError("Firebase credentials not found in environment variables")

# Parse the JSON string to a Python dictionary
cred_dict = json.loads(firebase_credentials_json)

# Initialize Firebase with the credentials
cred = credentials.Certificate(cred_dict)
firebase_app = firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
})

router = APIRouter()

# POST ROUTE for uploading a file to Firebase Storage
@router.post("/upload")
async def create_upload_file(file: UploadFile = File(...), path: Optional[str] = None):
    # Ensure the file is an image
    if not file.filename.endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Set the path for the file, default to the filename if not provided
    if not path:
        path = file.filename
    
    # Get the Firebase storage bucket and upload the file
    bucket = storage.bucket()
    blob = bucket.blob(path)
    blob.upload_from_string(await file.read(), content_type=file.content_type)

    # Generate the public URL for the uploaded file
    url = blob.public_url
    return {"url": url}
