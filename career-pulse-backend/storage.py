from google.cloud import storage
import json
from datetime import datetime

BUCKET_NAME = "career-pulse-data-praveen-space"

def get_bucket():
    client = storage.Client(project="praveen-space")
    try:
        bucket = client.get_bucket(BUCKET_NAME)
    except:
        bucket = client.create_bucket(BUCKET_NAME, location="us-central1")
    return bucket

def save_user_profile(email, name, skills):
    bucket = get_bucket()
    blob = bucket.blob(f"users/{email}/profile.json")
    data = {
        "email": email,
        "name": name,
        "skills": [s.strip() for s in skills.split(",")],
        "created_at": datetime.now().isoformat()
    }
    blob.upload_from_string(json.dumps(data))
    return True

def get_user_profile(email):
    bucket = get_bucket()
    blob = bucket.blob(f"users/{email}/profile.json")
    if blob.exists():
        return json.loads(blob.download_as_string())
    return None

def get_all_users():
    bucket = get_bucket()
    blobs = bucket.list_blobs(prefix="users/")
    users = []
    for blob in blobs:
        if blob.name.endswith("profile.json"):
            email = blob.name.split("/")[1]
            users.append(email)
    return users

def save_jobs_for_user(email, jobs, date_str):
    bucket = get_bucket()
    blob = bucket.blob(f"users/{email}/jobs/{date_str}.json")
    blob.upload_from_string(json.dumps(jobs))

def get_jobs_for_user(email, date_str):
    bucket = get_bucket()
    blob = bucket.blob(f"users/{email}/jobs/{date_str}.json")
    if blob.exists():
        return json.loads(blob.download_as_string())
    return []
