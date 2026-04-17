import unittest
from summarizer import parse_meeting_text, generate_markdown_summary

class TestSummarizer(unittest.TestCase):
    def test_parse_decisions(self):
        """Test extraction of decisions."""
        text = "Decision: We will use Python.\nOther text.\nDecided: Launch next week."
        parsed = parse_meeting_text(text)
        self.assertEqual(len(parsed['decisions']), 2)
        self.assertIn("We will use Python.", parsed['decisions'])
        self.assertIn("Launch next week.", parsed['decisions'])

    def test_parse_action_items(self):
        """Test extraction of action items with owners and deadlines."""
        text = "Action: Fix the UI @Alice by Friday\nTodo: Write tests @Bob by Monday"
        parsed = parse_meeting_text(text)
        
        self.assertEqual(len(parsed['action_items']), 2)
        
        alice_task = next(t for t in parsed['action_items'] if t['owner'] == 'Alice')
        self.assertEqual(alice_task['deadline'], 'friday')
        self.assertEqual(alice_task['task'], 'Fix the UI')
        
        bob_task = next(t for t in parsed['action_items'] if t['owner'] == 'Bob')
        self.assertEqual(bob_task['deadline'], 'monday')
        self.assertEqual(bob_task['task'], 'Write tests')
        
    def test_generate_markdown_summary(self):
        """Test markdown text generation."""
        parsed = {
            'decisions': ['Migrate to cloud'],
            'action_items': [{'task': 'Setup AWS', 'owner': 'Bob', 'deadline': 'Monday'}]
        }
        md = generate_markdown_summary("Weekly Sync", parsed)
        self.assertIn("# Meeting Summary: Weekly Sync", md)
        self.assertIn("- Migrate to cloud", md)
        self.assertIn("- [ ] **Setup AWS** (Owner: @Bob, Deadline: Monday)", md)

if __name__ == '__main__':
    unittest.main()
