# ContextKeeper

ContextKeeper is a Google Services-integrated smart assistant designed to help remote workers and students automate the organizing of daily meeting notes, action items, and calendar events. 

Remote workers waste 2+ hours daily formatting meeting notes, tracking tasks, and manual follow-ups. ContextKeeper solves this by using offline-first NLP to extract insights. Everything runs locally on your machine—Google APIs are only queried when explicitly told to.

## Features
- **Context-aware Summarizer**: Feed it meeting transcripts or notes; it will extract decisions and action items, save a cleanly formatted Markdown report back to Google Drive, and draft a follow-up Google Calendar event automatically.
- **Daily Briefing**: Check upcoming calendar events for the day and skim unread emails directly from your terminal.

## Requirements
- Python 3.8+
- Google Workspace account
- OAuth consent screen configured for Desktop client.

## Setup Instructions
1. Enable the following APIs in your Google Cloud Console:
   - Google Calendar API
   - Gmail API
   - Google Drive API
2. Create Desktop Client credentials and download them as `credentials.json` into the root of this project.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` if you have specific timezone configuration.

## Example Commands

**1. Create a detailed meeting summary and follow-up**
```bash
python main.py summarize --file meeting.txt
```
*Note: This will read local `meeting.txt`, upload `summary_meeting.md` to Drive, and prepare a calendar draft event.*

**2. Generate Daily Briefing**
```bash
python main.py briefing
```
*Note: This will list today's calendar events and unread inbox messages from Gmail.*

## Assumptions
- Uses standard user Google Auth flows (`InstalledAppFlow`). 
- On first run, a browser tab will open asking you to authenticate. After completion, a `token.json` is saved locally so you do not have to authenticate again.
- API quota limitations require credentials setup with your own client ID instead of a public shared instance.