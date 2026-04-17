import requests
import pandas as pd
from datetime import datetime

def fetch_remotive_jobs():
    try:
        response = requests.get("https://remotive.com/api/remote-jobs", timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            for job in data.get('jobs', [])[:50]:
                jobs.append({
                    'title': job.get('title', ''),
                    'company': job.get('company_name', ''),
                    'description': job.get('description', ''),
                    'url': job.get('url', ''),
                    'posted_date': job.get('publication_date', datetime.now().isoformat()),
                    'source': 'Remotive'
                })
            return pd.DataFrame(jobs)
    except Exception as e:
        print(f"Remotive API error: {e}")
    return pd.DataFrame()

def fetch_github_jobs():
    try:
        response = requests.get("https://jobs.github.com/positions.json?description=&location=remote", timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            for job in data[:50]:
                jobs.append({
                    'title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'description': job.get('description', ''),
                    'url': job.get('url', ''),
                    'posted_date': job.get('created_at', datetime.now().isoformat()),
                    'source': 'GitHub'
                })
            return pd.DataFrame(jobs)
    except Exception as e:
        print(f"github Jobs API error: {e}")
    return pd.DataFrame()

def fetch_all_jobs():
    remotive_df = fetch_remotive_jobs()
    github_df = fetch_github_jobs()
    if not remotive_df.empty and not github_df.empty:
        return pd.concat([remotive_df, github_df], ignore_index=True)
    elif not remotive_df.empty:
        return remotive_df
    elif not github_df.empty:
        return github_df
    else:
        return pd.DataFrame()
