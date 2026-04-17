from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import get_google_services
from summarizer import extract_meeting_data
import os

app = FastAPI(title="ContextKeeper Assistant")

class MeetingRequest(BaseModel):
    text: str
    save_to_drive: Optional[bool] = True

@app.get("/")
def root():
    return {"message": "ContextKeeper Assistant is running!", "status": "healthy"}

@app.post("/summarize")
async def summarize_meeting(request: MeetingRequest):
    try:
        calendar, drive = get_google_services()
        result = extract_meeting_data(request.text)
        
        if result.get("calendar_event"):
            event = calendar.events().insert(
                calendarId='primary',
                body=result["calendar_event"]
            ).execute()
            result["calendar_link"] = event.get("htmlLink")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
