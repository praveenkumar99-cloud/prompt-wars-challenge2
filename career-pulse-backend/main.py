from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from fastapi.middleware.cors import CORSMiddleware
import os

from storage import save_user_profile, get_user_profile, get_all_users, save_jobs_for_user, get_jobs_for_user
from job_fetcher import fetch_all_jobs
from job_matcher import filter_and_sort_jobs

app = FastAPI(title="CareerPulse Job Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterRequest(BaseModel):
    email: str
    name: str
    skills: str

class JobsResponse(BaseModel):
    email: str
    date: str
    jobs: List[dict]

@app.get("/")
def root():
    return {"message": "CareerPulse Job Agent is running", "status": "healthy"}

@app.post("/api/register")
def register_user(request: RegisterRequest):
    try:
        save_user_profile(request.email, request.name, request.skills)
        return {"status": "success", "message": f"User {request.email} registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/profile/{email}")
def get_profile(email: str):
    profile = get_user_profile(email)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile

@app.get("/api/jobs/{email}")
def get_jobs(email: str):
    today = str(date.today())
    jobs = get_jobs_for_user(email, today)
    if not jobs:
        return {"email": email, "date": today, "jobs": []}
    return {"email": email, "date": today, "jobs": jobs}

@app.get("/api/daily-process")
def daily_job_processor():
    """Endpoint called by Cloud Scheduler daily"""
    users = get_all_users()
    if not users:
        return {"status": "no_users", "message": "No registered users"}
    
    all_jobs = fetch_all_jobs()
    if all_jobs.empty:
        return {"status": "no_jobs", "message": "No jobs fetched"}
    
    processed = 0
    for email in users:
        profile = get_user_profile(email)
        if not profile:
            continue
        user_skills = profile.get('skills', [])
        matched_jobs = filter_and_sort_jobs(all_jobs, user_skills)
        if matched_jobs:
            save_jobs_for_user(email, matched_jobs, str(date.today()))
            processed += 1
    
    return {"status": "success", "message": f"Processed {processed} users", "total_users": len(users)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
