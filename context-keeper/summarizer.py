import re

def parse_meeting_text(text):
    """
    Extracts decisions, action items, owners, and deadlines using simple heuristics.
    In a true NLP system, this would use a model like spaCy or a local LLM.
    """
    decisions = []
    action_items = []
    
    lines = text.split('\n')
    for line in lines:
        lower_line = line.lower()
        if 'decision:' in lower_line or 'decided:' in lower_line:
            idx = max(lower_line.find('decision:'), lower_line.find('decided:'))
            content = line[idx:].split(':', 1)[-1].strip()
            if content:
                decisions.append(content)
        
        if 'action:' in lower_line or 'todo:' in lower_line or 'to-do:' in lower_line:
            # We look for "[Task] @[Owner] by [Deadline]" patterns conceptually
            idx = max(lower_line.find('action:'), lower_line.find('todo:'), lower_line.find('to-do:'))
            content = line[idx:].split(':', 1)[-1].strip()
            
            # Very basic extraction for owner (e.g. @Alice) and deadline (e.g. by Friday)
            owner = "Unassigned"
            deadline = "No deadline"
            owner_match = re.search(r'@(\w+)', content)
            if owner_match:
                owner = owner_match.group(1)
                content = content.replace(owner_match.group(0), '').strip()
                
            deadline_match = re.search(r'by\s+(\w+)', lower_line)
            if deadline_match:
                deadline = deadline_match.group(1)
                content = re.sub(r'(?i)\s*by\s+' + deadline, '', content).strip()
            
            if content:
                action_items.append({'task': content, 'owner': owner, 'deadline': deadline})
                
    return {
        'decisions': decisions,
        'action_items': action_items
    }

def generate_markdown_summary(topic, parsed_data):
    """Generates the Markdown output."""
    md = f"# Meeting Summary: {topic}\n\n"
    md += "## Decisions Made\n"
    if not parsed_data['decisions']:
        md += "- None explicitly recorded.\n"
    for d in parsed_data['decisions']:
        md += f"- {d}\n"
        
    md += "\n## Action Items\n"
    if not parsed_data['action_items']:
        md += "- None explicitly recorded.\n"
    for item in parsed_data['action_items']:
        md += f"- [ ] **{item['task']}** (Owner: @{item['owner']}, Deadline: {item['deadline']})\n"
        
    return md
