# UV integration ?
#1. Create a lock file via push - will fail if updated by someone else
#2. read state from repo via API
#3. IF state needs to change, write state back to repo via force push
#4. Remove lockfile

#import os
import time
import smtplib
from pynput import mouse, keyboard
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
from datetime import datetime
#import requests
#import base64

from dotenv import dotenv_values, find_dotenv

# [active]->-send inactive->-[inactive]->-event->-[waking]->-send wake->-[active]

# --- Settings ---
env = dotenv_values(find_dotenv())
CHECK_INTERVAL = int(env['CHECK_INTERVAL_SECONDS']) 
ALERT_INTERVAL = int(env['ALERT_INTERVAL_SECONDS']) 
EMAIL_ADDRESS = env['SENDER_EMAIL_ADDRESS']
EMAIL_PASSWORD = env['SENDER_EMAIL_PASSWORD']
RECIPIENT_EMAIL = env['RECIPIENT_EMAIL_ADDRESS']
REPO_URL = env['REPO_URL']
GITHUB_TOKEN = env['GITHUB_TOKEN']
BRANCH = env['BRANCH']
TIMESTAMP_FILE = env['TIMESTAMP_FILE']
STATE_FILE = env['STATE_FILE']

# --- StateMachine Class ---
class StateMachine:
    def __init__(self, alert_interval):
        self.last_activity = time.time
        self.alert_interval = alert_interval
        self.state = 'active'

    @property
    def state(self):
        """
        returns the content of the repository state file (STATE_FILE).
        STATE_FILE is configurable in the .env file.
        
        Returns:
            str: The content of the state file if successful, None otherwise.
        """
        try:
            self.pull_from_repo()
            with open(STATE_FILE, "r", encoding="utf-8") as file:
                return file.read().strip()
        except:
            return None

    @state.setter
    def state(self, state):
        with open(STATE_FILE, "w") as f:
            f.write(state)
        self.push_to_repo(STATE_FILE)

    @property
    def timestamp(self):
        """Update the timestamp file with and return current timestamp."""
        timestamp = datetime.now().isoformat()
        with open(TIMESTAMP_FILE, "w") as f:
            f.write(timestamp)
        return timestamp

    def update_activity(self):
        """Update the last activity timestamp and handle waking state."""
        self.last_activity = time.time
        if self.state == "inactive":
            self.update_state("waking")

    def check_inactivity(self):
        """Check for inactivity and transition states."""
        current_time = time.time()
        if current_time - self.last_activity > self.alert_interval:
            self.update_state("inactive")
            self.push_to_repo([STATE_FILE])
        elif self.state == "waking":
        #    self.update_state("active")
            self.timestamp
            self.push_to_repo([STATE_FILE, TIMESTAMP_FILE])
        else:
            self.timestamp
            self.push_to_repo([STATE_FILE, TIMESTAMP_FILE])

    def pull_from_repo(self):
        subprocess.run(["git", "pull"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def push_to_repo(self, file):
        """Push updates to the repository."""
        repo_url_with_token = REPO_URL.replace("https://", f"https://{GITHUB_TOKEN}@")
        try:
            self.timestamp
            subprocess.run(["git", "commit", "-a", "-m", f"auto-update of {file}"], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # force push is safe as knowledge of current state is updated from the repo file via API
            subprocess.run(["git", "push", "--force", repo_url_with_token, BRANCH],  check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Failed to push changes: {e}")

    def send_email(self, subject, body):
        """Send an email notification."""
        try:
            msg = MIMEMultipart()
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = RECIPIENT_EMAIL
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            # Connect to the mail server
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f"Email sent: {body}")
        except Exception as e:
            print(f"Failed to send email: {e}")


# --- Main Application ---
def main():

    state_machine = StateMachine(ALERT_INTERVAL)

    # Listener for keyboard and mouse activity
    def on_activity(*args):
        state_machine.update_activity()
        
    # Setup listeners
    keyboard_listener = keyboard.Listener(on_press=on_activity)
    mouse_listener = mouse.Listener(on_move=on_activity)

    keyboard_listener.start()
    mouse_listener.start()

    # Periodically check inactivity
    while True:
        print(state_machine.state)
        #state_machine.state = 'blob'
        #exit()
        state_machine.check_inactivity()
        time.sleep(CHECK_INTERVAL)  # Check more frequently than the alert threshold


if __name__ == "__main__":
    main()


# STATE_URL = env['STATE_URL']
#
# subprocess.run(["git", "add", file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#
#    def push_to_repo(self, file_list):
#        """Push updates to the repository."""
#        repo_url_with_token = REPO_URL.replace("https://", f"https://{GITHUB_TOKEN}@")
#        try:
#            subprocess.run(["git", "add", *file_list], 
#                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
#            subprocess.run(["git", "commit", "-m", f"auto-update of {STATE_FILE} and {TIMESTAMP_FILE}"],
#                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            # force push is safe as knowledge of current state is updated from the repo file via API
#            subprocess.run(["git", "push", "--force", repo_url_with_token, BRANCH], 
#                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
#            print("Changes pushed successfully!")
#        except subprocess.CalledProcessError as e:
#            print(f"Failed to push changes: {e}")



#    def rest_get_state(self):
#        """
#        returns the content of the repository state file located at STATE_URL.
#        STATE_URL is configurable in the .env file.
#        
#        Returns:
#            str: The content of the state file if successful, None otherwise.
#        """
#        headers = {
#            "Authorization": f"Bearer {GITHUB_TOKEN}",
#            "Cache-Control": "no-cache"
#        } if GITHUB_TOKEN else {}
#
#        self.pull_from_repo()
#        with open(STATE_FILE, "r", encoding="utf-8") as file:
#            print(file.read().strip())
#            print("hello")
#        exit()
#
#        # Fetch state file metadata
#        response = requests.get(f"{STATE_URL}?token={time.time()}", headers=headers)
#        if response.status_code != 200:
#            print(f"Error fetching file metadata: {response.status_code}")
#            return None
#
#        try:
#            # Parse the metadata and extract the download URL and SHA
#            data = response.json()
#            file_content_url = data.get("download_url")
#
#            if not file_content_url:
#                print("Download URL not found in response.")
#                return None
#
#            # Fetch raw file content
#            file_response = requests.get(file_content_url)
#            if file_response.status_code == 200:
#                return file_response.text
#            else:
#                print(f"Error fetching raw file content: {file_response.status_code}")
#                return None
#        except (ValueError, KeyError) as e:
#            print(f"Error parsing response: {e}")
#            return None
#
#    def rest_put_state(self, state):
#        headers = {
#            "Authorization": f"Bearer {GITHUB_TOKEN}",
#            "Accept": "application/vnd.github+json"
#        } if GITHUB_TOKEN else {}
#
#        # File content and commit message
#        content = state
#        encoded_content = base64.b64encode(content.encode()).decode()
#        commit_message = f"updating state to {state}"
#        state_sha = self.state_sha
#
#        # Create or update the file
#        data = {
#            "message": commit_message,
#            "content": encoded_content,
#            "branch": BRANCH
#        }
#        if state_sha:
#            data["sha"] = state_sha # if updating, include the SHA
#
#        response = requests.put(STATE_URL, headers=headers, json=data)
#
#        if response.status_code in (200, 201):
#            return state
#        else:
#            print("Failed to update file:", response.json())
#
#    @property
#    def state_sha(self):
#        """
#        returns the SHA of the repository state file located at STATE_URL.
#        STATE_URL is configurable in the .env file.
#        
#        Returns:
#            str: The SHA of the state file if successful, None otherwise.
#        """
#        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
#
#        # Fetch state file metadata
#        response = requests.get(STATE_URL, headers=headers)
#        if response.status_code != 200:
#            print(f"Error fetching file metadata: {response.status_code}")
#            return None
#
#        try:
#            # Parse the metadata and extract the download URL and SHA
#            data = response.json()
#            state_sha = data.get("sha") 
#
#            if not state_sha:
#                print("SHA not found in response.")
#                return None
#            else:
#                return state_sha
#
#        except (ValueError, KeyError) as e:
#            print(f"Error parsing response: {e}")
#            return None


#    def update_state(self, new_state):
#        """Change state and perform actions if necessary."""
#        # only act on state CHANGE
#        if new_state == "inactive" and self.state == "active":
#            self.send_email(
#                "User Inactivity Alert",
#                f"No user activity detected in the past {self.alert_interval} seconds.",
#            )
#        # only act on state CHANGE
#        elif new_state == "waking" and self.state == "inactive":
#            self.send_email("User Waking Alert", "User has woken up.")
#        self.state = new_state
#        with open(STATE_FILE, "w") as f:
#            f.write(f"{self.state}\n")