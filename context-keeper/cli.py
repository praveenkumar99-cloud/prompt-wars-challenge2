import argparse
import sys
import os

from summarizer import parse_meeting_text, generate_markdown_summary
from google_drive import save_to_drive
from google_calendar import get_today_events, create_draft_event
from gmail_reader import get_unread_emails

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def summarize_command(args):
    print(f"{Colors.OKBLUE}ContextKeeper: Summarizing meeting notes...{Colors.ENDC}")
    if not os.path.exists(args.file):
        print(f"{Colors.FAIL}Error: File {args.file} not found.{Colors.ENDC}")
        sys.exit(1)
        
    with open(args.file, 'r', encoding='utf-8') as f:
        text = f.read()
        
    parsed = parse_meeting_text(text)
    topic = os.path.basename(args.file).split('.')[0].replace('_', ' ').title()
    md_content = generate_markdown_summary(topic, parsed)
    
    print(f"{Colors.OKGREEN}Summary generated.{Colors.ENDC}")
    print(md_content)
    
    file_name = f"summary_{topic.replace(' ', '_')}.md"
    print(f"{Colors.OKBLUE}Uploading to Google Drive...{Colors.ENDC}")
    result = save_to_drive(file_name, md_content)
    if result:
        print(f"{Colors.OKGREEN}Successfully saved {file_name} to Drive (ID: {result.get('id')}).{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}Failed to upload to Drive.{Colors.ENDC}")
        
    if parsed['action_items']:
        print(f"{Colors.OKBLUE}Suggesting a follow-up meeting to check on action items...{Colors.ENDC}")
        event = create_draft_event(f"Follow up: {topic}", "Checking status of action items.")
        if event:
            print(f"{Colors.OKGREEN}Created follow-up draft event on Google Calendar: {event.get('htmlLink')}{Colors.ENDC}")
            

def briefing_command(args):
    print(f"{Colors.HEADER}{Colors.BOLD}ContextKeeper: Daily Briefing{Colors.ENDC}\n")
    
    print(f"{Colors.OKCYAN}Fetching today's calendar events...{Colors.ENDC}")
    events = get_today_events()
    if not events:
        print("No upcoming events found for today.")
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"- {Colors.WARNING}{start}{Colors.ENDC}: {event.get('summary')}")
            
    print(f"\n{Colors.OKCYAN}Checking unread emails...{Colors.ENDC}")
    emails = get_unread_emails(max_results=5)
    if not emails:
        print("No unread emails.")
    else:
        for email in emails:
            print(f"- From {Colors.OKBLUE}{email['from']}{Colors.ENDC} | {email['subject']}")
            
    print(f"\n{Colors.OKGREEN}Today's Focus:{Colors.ENDC}")
    print("- Prepare for upcoming meetings.")
    print("- Respond to high-priority emails.")
    print("- Complete pending action items from yesterday.")

def create_parser():
    parser = argparse.ArgumentParser(description="ContextKeeper - Smart assistant for remote workers")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # summarize command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize a meeting transcript and upload to Drive")
    summarize_parser.add_argument("--file", required=True, help="Path to the text file containing the transcript")
    
    # briefing command
    briefing_parser = subparsers.add_parser("briefing", help="Generate a daily briefing from Calendar and Gmail")
    
    return parser

def run_cli():
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == "summarize":
        summarize_command(args)
    elif args.command == "briefing":
        briefing_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    run_cli()
