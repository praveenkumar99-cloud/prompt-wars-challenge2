from fastapi import FastAPI, BackgroundTasks
from task_generator import TaskGenerator
from datetime import datetime
import os

app = FastAPI(title="AutoTracker API")

@app.get("/")
def root():
    return {"message": "AutoTracker is running", "status": "healthy"}

@app.get("/api/tasks")
def get_tasks():
    """Get current task list"""
    generator = TaskGenerator()
    tasks = generator.generate_tasks()
    return {"tasks": tasks, "generated_at": datetime.now().isoformat()}

@app.post("/api/refresh")
def refresh_tasks(background_tasks: BackgroundTasks):
    """Trigger task refresh (called by Cloud Scheduler)"""
    background_tasks.add_task(process_tasks)
    return {"status": "processing"}

def process_tasks():
    """Process tasks in background"""
    generator = TaskGenerator()
    tasks = generator.generate_tasks()
    # Save to Cloud Storage for dashboard to read
    # from storage import save_tasks
    # save_tasks(tasks)
    pass
