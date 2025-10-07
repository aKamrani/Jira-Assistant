#!/usr/bin/env python3
"""
Jira Sub-task Creator and Work Logger

This script creates sub-tasks for a parent Jira issue and logs work for each sub-task.
It uses the official Jira REST API for better reliability and error handling.

The parent issue key is automatically determined based on the CSV filename:
- Files containing 'maintenance' -> uses MAINTENANCE_PARENT_ISSUE_KEY
- Files containing 'develop' -> uses DEVELOP_PARENT_ISSUE_KEY

Usage: python jira-subtask-creator.py <input_file.csv>
Examples:
  python jira-subtask-creator.py maintenance-subtasks.csv
  python jira-subtask-creator.py develop-subtasks.csv
"""

import sys
import os
import csv
import time
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv()

class JiraSubtaskCreatorV2:
    def __init__(self):
        self.base_url = os.getenv('JIRA_BASE_URL', 'https://jira.avakatan.ir')
        self.token = os.getenv('JIRA_TOKEN')
        self.assignee_username = os.getenv('ASSIGNEE_USERNAME', 'a.kamrani')
        
        # Parent issue keys for different types
        self.maintenance_parent_key = os.getenv('MAINTENANCE_PARENT_ISSUE_KEY', 'BM-5610')
        self.develop_parent_key = os.getenv('DEVELOP_PARENT_ISSUE_KEY', 'BM-5611')
        
        # Will be set based on CSV filename
        self.parent_issue_key = None
        
        if not self.token:
            raise ValueError("JIRA_TOKEN not found in environment variables")
        
        self.session = requests.Session()
        
        # Try different authentication methods
        # Method 1: Bearer token (if it's a session token)
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Method 2: Basic Auth with username and token (backup)
        self.basic_auth = HTTPBasicAuth('a.kamrani', self.token)
        
        # Cache for project and component IDs
        self.project_id = None
        self.devops_component_id = None
        self.subtask_issue_type_id = None
    
    def determine_parent_issue_key(self, csv_filename):
        """Determine parent issue key based on CSV filename"""
        filename_lower = csv_filename.lower()
        
        if 'maintenance' in filename_lower:
            self.parent_issue_key = self.maintenance_parent_key
            print(f"Detected maintenance tasks - using parent: {self.parent_issue_key}")
        elif 'develop' in filename_lower:
            self.parent_issue_key = self.develop_parent_key
            print(f"Detected development tasks - using parent: {self.parent_issue_key}")
        else:
            # Fallback to maintenance if filename doesn't match
            self.parent_issue_key = self.maintenance_parent_key
            print(f"Filename doesn't match 'maintenance' or 'develop' - defaulting to maintenance parent: {self.parent_issue_key}")
        
        return self.parent_issue_key
        
    def get_project_info(self):
        """Get project information and cache IDs"""
        if self.project_id:
            return True
            
        url = f"{self.base_url}/rest/api/2/project/BM"
        response = self.session.get(url)
        
        if response.status_code == 200:
            project_data = response.json()
            self.project_id = project_data['id']
            print(f"Project ID: {self.project_id}")
            
            # Get DevOps component ID
            for component in project_data.get('components', []):
                if component['name'] == 'DevOps':
                    self.devops_component_id = component['id']
                    print(f"DevOps Component ID: {self.devops_component_id}")
                    break
            
            # Get sub-task issue type ID
            for issue_type in project_data.get('issueTypes', []):
                if issue_type['name'] == 'Sub-task':
                    self.subtask_issue_type_id = issue_type['id']
                    print(f"Sub-task Issue Type ID: {self.subtask_issue_type_id}")
                    break
            
            return True
        else:
            print(f"Failed to get project info. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def parse_time_estimate(self, time_str):
        """Parse time estimate string (e.g., '6h', '4h 30m') to seconds"""
        if not time_str:
            return None
            
        # Remove spaces and convert to lowercase
        time_str = time_str.replace(' ', '').lower()
        
        total_seconds = 0
        
        # Parse hours
        hours_match = re.search(r'(\d+)h', time_str)
        if hours_match:
            total_seconds += int(hours_match.group(1)) * 3600
        
        # Parse minutes
        minutes_match = re.search(r'(\d+)m', time_str)
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60
        
        # Parse days
        days_match = re.search(r'(\d+)d', time_str)
        if days_match:
            total_seconds += int(days_match.group(1)) * 8 * 3600  # 8 hours per day
        
        # Parse weeks
        weeks_match = re.search(r'(\d+)w', time_str)
        if weeks_match:
            total_seconds += int(weeks_match.group(1)) * 5 * 8 * 3600  # 5 days per week, 8 hours per day
        
        return total_seconds if total_seconds > 0 else None
    
    def create_subtask(self, summary, original_estimate):
        """Create a sub-task using Jira REST API"""
        if not self.get_project_info():
            return None
        
        # Parse time estimate
        time_seconds = self.parse_time_estimate(original_estimate)
        
        # Prepare issue data
        issue_data = {
            "fields": {
                "project": {
                    "id": self.project_id
                },
                "parent": {
                    "key": self.parent_issue_key
                },
                "issuetype": {
                    "id": self.subtask_issue_type_id
                },
                "summary": summary,
                "assignee": {
                    "name": self.assignee_username
                },
                "labels": ["DevOps"]
            }
        }
        
        # Add component if found
        if self.devops_component_id:
            issue_data["fields"]["components"] = [{"id": self.devops_component_id}]
        
        # Add time tracking if estimate is provided
        if time_seconds:
            issue_data["fields"]["timetracking"] = {
                "originalEstimate": original_estimate
            }
        
        url = f"{self.base_url}/rest/api/2/issue"
        response = self.session.post(url, json=issue_data)
        
        if response.status_code == 201:
            issue_data = response.json()
            issue_key = issue_data['key']
            print(f"Created sub-task: {issue_key}")
            return issue_key
        else:
            print(f"Failed to create sub-task. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def log_work(self, issue_key, time_spent, work_description):
        """Log work using Jira REST API"""
        # Parse time to seconds
        time_seconds = self.parse_time_estimate(time_spent)
        if not time_seconds:
            print(f"Invalid time format: {time_spent}")
            return False
        
        # Calculate start time (current time minus the work duration)
        start_time = datetime.now() - timedelta(seconds=time_seconds)
        
        worklog_data = {
            "timeSpent": time_spent,
            "started": start_time.strftime("%Y-%m-%dT%H:%M:%S.000+0330"),  # Tehran timezone
            "comment": work_description
        }
        
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/worklog"
        response = self.session.post(url, json=worklog_data)
        
        if response.status_code == 201:
            print(f"Logged work for {issue_key}: {time_spent}")
            return True
        else:
            print(f"Failed to log work for {issue_key}. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def set_status_to_done(self, issue_key):
        """Set the status of a sub-task to Done using Jira REST API"""
        # Get available transitions
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions"
        response = self.session.get(url)
        
        if response.status_code != 200:
            print(f"Failed to get transitions for {issue_key}")
            return False
        
        transitions = response.json().get('transitions', [])
        done_transition = None
        
        # Look for "Done" transition
        for transition in transitions:
            if transition['name'].lower() in ['done', 'complete', 'closed']:
                done_transition = transition
                break
        
        if not done_transition:
            print(f"No 'Done' transition found for {issue_key}")
            print(f"Available transitions: {[t['name'] for t in transitions]}")
            return False
        
        # Execute the transition
        transition_data = {
            "transition": {
                "id": done_transition['id']
            }
        }
        
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions"
        response = self.session.post(url, json=transition_data)
        
        if response.status_code == 204:
            print(f"Set status to '{done_transition['name']}' for {issue_key}")
            return True
        else:
            print(f"Failed to set status for {issue_key}. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def test_connection(self):
        """Test connection to Jira with multiple authentication methods"""
        url = f"{self.base_url}/rest/api/2/myself"
        
        # Try Bearer token first
        response = self.session.get(url)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"Connected as: {user_data['displayName']} ({user_data['emailAddress']})")
            return True
        
        # If Bearer token fails, try Basic Auth
        print("Bearer token failed, trying Basic Auth...")
        self.session.auth = self.basic_auth
        response = self.session.get(url)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"Connected as: {user_data['displayName']} ({user_data['emailAddress']})")
            return True
        
        # If both fail, try with email as username
        print("Basic Auth with username failed, trying with email...")
        email_auth = HTTPBasicAuth('a.kamrani@domil.io', self.token)
        self.session.auth = email_auth
        response = self.session.get(url)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"Connected as: {user_data['displayName']} ({user_data['emailAddress']})")
            return True
        
        print(f"All authentication methods failed. Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        return False
    
    def process_tasks(self, input_file):
        """Process all tasks from the input file"""
        if not os.path.exists(input_file):
            print(f"Input file {input_file} not found")
            return
        
        # Determine parent issue key based on filename
        self.determine_parent_issue_key(input_file)
        
        # Test connection first
        print("Testing connection to Jira...")
        if not self.test_connection():
            print("Failed to connect to Jira. Please check your credentials.")
            return
        
        created_tasks = []
        
        with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                summary = row['Summary'].strip()
                original_estimate = row['Original Estimate'].strip()
                
                if not summary or not original_estimate:
                    print(f"Skipping row with missing data: {row}")
                    continue
                
                print(f"\nProcessing: {summary}")
                
                # Create sub-task
                issue_key = self.create_subtask(summary, original_estimate)
                if issue_key:
                    created_tasks.append(issue_key)
                    
                    # Wait a moment before logging work
                    time.sleep(2)
                    
                    # Log work
                    if self.log_work(issue_key, original_estimate, summary):
                        # Wait a moment before setting status
                        time.sleep(2)
                        
                        # Set status to Done
                        self.set_status_to_done(issue_key)
                
                # Wait between tasks to avoid rate limiting
                time.sleep(3)
        
        print(f"\nCompleted processing. Created {len(created_tasks)} sub-tasks:")
        for task in created_tasks:
            print(f"  - {task}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python jira-subtask-creator.py <input_file.csv>")
        print("Examples:")
        print("  python jira-subtask-creator.py maintenance-subtasks.csv")
        print("  python jira-subtask-creator.py develop-subtasks.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        creator = JiraSubtaskCreatorV2()
        creator.process_tasks(input_file)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
