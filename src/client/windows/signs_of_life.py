# Capture this error and report to the user by EMAIL!!!
#
# To https://github.com/LaurenceMolloy/SignsOfLife.git
#  ! [remote rejected] main -> main (refusing to allow a Personal Access Token to create or update workflow `.github/workflows/combine_states.yml` without `workflow` scope)
# error: failed to push some refs to 'https://github.com/LaurenceMolloy/SignsOfLife.git'
# Failed to push changes: Command '['git', 'push', '--force', 'https://<GITHUB_PAT>@github.com/LaurenceMolloy/SignsOfLife.git', 'main']' returned non-zero exit status 1.

import time
import subprocess
from pynput import mouse, keyboard
from datetime import datetime
from dotenv import dotenv_values, find_dotenv

# --- Settings ---
env = dotenv_values(find_dotenv())
CHECK_INTERVAL = int(env['CHECK_INTERVAL_SECONDS']) 
ALERT_INTERVAL = int(env['ALERT_INTERVAL_SECONDS']) 
REPO_URL = env['REPO_URL']
GITHUB_TOKEN = env['GITHUB_TOKEN']
BRANCH = env['BRANCH']
HEARTBEAT_FILE = env['HEARTBEAT_FILE']
STATE_FILE = env['STATE_FILE']

# --- StateMachine Class ---
class StateMachine:
    def __init__(self, alert_interval):
        self.last_activity = time.time()
        self.alert_interval = alert_interval
        self.local_state = 'active'
        self.remote_state = self.local_state

    @property
    def remote_state(self):
        pass

    @remote_state.setter
    def remote_state(self, state):
        with open(STATE_FILE, "w") as f:
            f.write(state)
        self.push_to_remote(STATE_FILE)

    @property
    def heartbeat(self):
        """Update the heartbeat file with and return current timestamp."""
        timestamp = datetime.now().isoformat()
        with open(HEARTBEAT_FILE, "w") as f:
            f.write(timestamp)
        return timestamp

    def update_activity(self):
        """Update the last activity timestamp""" # and handle waking state."""
        self.last_activity = time.time()
#        self.local_state = "active"
#        if self.local_state == "inactive":
#            self.local_state = "waking"

    def check_activity(self):
        """Check for inactivity and transition states."""
        if time.time() - self.last_activity > self.alert_interval:
            self.local_state = "inactive"
        else:
            self.local_state = "active"
        self.remote_state = self.local_state


    def push_to_remote(self, file):
        """Push updates to the repository."""
        repo_url_with_token = REPO_URL.replace("https://", f"https://{GITHUB_TOKEN}@")
        try:
            self.heartbeat
            subprocess.run(["git", "-C", '.', "add", "."], check=True)
            subprocess.run(["git", "commit", "-a", "-m", f"auto-update of {file}"], check=True)#,
#                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # force push is safe as knowledge of current state is updated from the repo file via API
            subprocess.run(["git", "push", "--force", repo_url_with_token, BRANCH],  check=True)#,
#                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Failed to push changes: {e}")


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
#        print(state_machine.remote_state)
        state_machine.check_activity()
        time.sleep(CHECK_INTERVAL)  # Check more frequently than the alert threshold


if __name__ == "__main__":
    main()


# STATE_URL = env['STATE_URL']
#
# subprocess.run(["git", "add", file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#
#    def push_to_remote(self, file_list):
#        """Push updates to the repository."""
#        repo_url_with_token = REPO_URL.replace("https://", f"https://{GITHUB_TOKEN}@")
#        try:
#            subprocess.run(["git", "add", *file_list], 
#                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
#            subprocess.run(["git", "commit", "-m", f"auto-update of {STATE_FILE} and {HEARTBEAT_FILE}"],
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
#        self.pull_from_remote()
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



            #self.update_state("inactive")
            #self.push_to_remote(STATE_FILE)
        #elif self.state == "waking":
        #    self.update_state("active")
            #self.timestamp
        #    self.push_to_remote(STATE_FILE)
        #else:
            #self.timestamp
        #    self.push_to_remote(STATE_FILE)




#    @property
#    def remote_state(self):
#        """
#        returns the content of the repository state file (STATE_FILE).
#        STATE_FILE is configurable in the .env file.
#        
#        Returns:
#            str: The content of the state file if successful, None otherwise.
#        """
#        try:
#            self.pull_from_remote()
#            with open(STATE_FILE, "r", encoding="utf-8") as file:
#                return file.read().strip()
#        except:
#            return None

#    def pull_from_remote(self):
#        subprocess.run(["git", "pull"], check=True,
#                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
