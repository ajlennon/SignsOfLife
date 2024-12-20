import os
import glob
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load the .env file only if it exists (local development)
if os.getenv("CI") is None:  # Typically, CICD systems set a CI environment variable
    load_dotenv(override=True)

# required for email alerts
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_ADDRESS = os.getenv('SENDER_EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('SENDER_EMAIL_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL_ADDRESS')
MAX_AGE_SECONDS = os.getenv("ALERT_INTERVAL_SECONDS")

# global state variables
STATE = "inactive"
ALIVE = False

def calculate_state(states_dir, state_file):
    """
    Calculate the overall state by logically combining individual states
    from state_*.txt files and write the result to a file.

    Args:
        states_dir (str): Directory containing state_*.txt files.
        state_file (str): Path to the output state file.
    """
    state_files = glob.glob(os.path.join(states_dir, "state_*.txt"))
    active, waking = False, False

    with open(state_file, "r") as f:
        current_state = f.read().strip().lower()

    for file in state_files:
        with open(file, "r") as f:
            content = f.read().strip().lower()
            active = active or (content == "active")
            waking = waking or (content == "waking")

    new_state = "active" if active else "waking" if waking else "inactive"

    with open(state_file, "w") as f:
        f.write(new_state)

    if current_state == 'active' and new_state != 'active':
        send_email(
            "Alert: User has gone to sleep",
            f"No user activity has been detected in the past {MAX_AGE_SECONDS} seconds. Please check in with user."
        )
    if current_state == 'inactive' and new_state != 'inactive':
        send_email(
            "Good News: User has woken up",
            "User activity has resumed. User is alive and well."
        )


def calculate_heartbeat(heartbeats_dir, heartbeat_file):
    """
    Check the recency of heartbeat timestamps from heartbeat_*.txt files
    and write the result (alive or not) to a file.

    Args:
        heartbeats_dir (str): Directory containing heartbeat_*.txt files.
        heartbeat_file (str): Path to the output heartbeat file.
    """
    heartbeat_files = glob.glob(os.path.join(heartbeats_dir, "heartbeat_*.txt"))
    current_heartbeat, new_heartbeat = False, False

    with open(heartbeat_file, "r") as f:
        current_heartbeat = f.read().strip().lower() == 'true'

    for file in heartbeat_files:
        with open(file, "r") as f:
            content = f.read().strip()
            if is_alive(content):
                new_heartbeat = True
                break  # Exit early if any device is alive

    with open(heartbeat_file, "w") as f:
        f.write(str(new_heartbeat))

    if (current_heartbeat) and (not new_heartbeat):
        send_email(
            "Alert: Devices Have Gone Offline",
            f"All devices have stopped sending heartbeats. No activity has been detected in the past {MAX_AGE_SECONDS} seconds. Please check the system immediately."
        )

    if (not current_heartbeat) and (new_heartbeat):
        send_email(
            "Good News: Devices Are Back Online",
            "Heartbeats from devices have resumed. All systems appear to be functioning normally."
        )


def is_alive(timestamp_string):
    """
    Determine if a device is alive based on the recency of its heartbeat.

    Args:
        timestamp_string (str): ISO format timestamp string.

    Returns:
        bool: True if the heartbeat is recent, False otherwise.
    """
    try:
        heartbeat_time = datetime.fromisoformat(timestamp_string)
        current_time = datetime.now()
        age_seconds = (current_time - heartbeat_time).total_seconds()
        return int(age_seconds) < int(MAX_AGE_SECONDS)
    except Exception:
        return False

def send_email(subject, body):
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


if __name__ == "__main__":

        # presumes script lives under REPO_ROOT/src/server
        repo_root = Path(__file__).parent.parent.parent

        states_dir = f"{repo_root}/data/states"
        state_file = f"{repo_root}/data/state.txt"
        calculate_state(states_dir, state_file)

        heartbeats_dir = f"{repo_root}/data/heartbeats"
        heartbeat_file = f"{repo_root}/data/heartbeat.txt"
        calculate_heartbeat(heartbeats_dir, heartbeat_file)
