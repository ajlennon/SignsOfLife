import os
import time
import smtplib
from pynput import mouse, keyboard
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
from datetime import datetime

from dotenv import dotenv_values, find_dotenv

# [active]->-send inactive->-[inactive]->-event->-[waking]->-send wake->-[active]

# File to update
TIMESTAMP_FILE = "last_active.txt"

# --- Settings ---
env = dotenv_values(find_dotenv())
CHECK_INTERVAL = int(env['CHECK_INTERVAL_SECONDS'])  # Inactivity threshold in seconds
ALERT_INTERVAL = int(env['ALERT_INTERVAL_SECONDS'])  # Inactivity threshold in seconds
EMAIL_ADDRESS = env['SENDER_EMAIL_ADDRESS']
EMAIL_PASSWORD = env['SENDEREMAIL_PASSWORD']  # Replace with app password
RECIPIENT_EMAIL = env['RECIPIENT_EMAIL_ADDRESS']

# --- StateMachine Class ---
class StateMachine:
    def __init__(self, alert_interval):
        self.state = "active"  # Initial state
        self.last_activity = time.time()
        self.alert_interval = alert_interval
        self.update_timestamp() # initialise timestamp upon start up

    def update_timestamp(self):
        with open(TIMESTAMP_FILE, "w") as f:
            current_time = datetime.now().isoformat()
            f.write(f"Last activity: {current_time}\n")

    def update_activity(self):
        """Update the last activity timestamp and handle waking state."""
        self.last_activity = time.time()
        if self.state == "inactive":
            self.change_state("waking")

    def change_state(self, new_state):
        """Change state and perform actions if necessary."""
        if new_state == "inactive" and self.state == "active":
            self.send_email(
                "User Inactivity Alert",
                f"No user activity detected in the past {self.alert_interval} seconds.",
            )
        elif new_state == "active" and self.state == "waking":
            self.send_email("User Waking Alert", "User has woken up.")
        self.state = new_state

    def check_inactivity(self):
        """Check for inactivity and transition states."""
        current_time = time.time()
        if current_time - self.last_activity > self.alert_interval:
            self.change_state("inactive")
        elif self.state == "waking":
            self.change_state("active")
            self.update_timestamp()
        else:
            self.update_timestamp()

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
        state_machine.check_inactivity()
        time.sleep(CHECK_INTERVAL)  # Check more frequently than the alert threshold


if __name__ == "__main__":
    main()
