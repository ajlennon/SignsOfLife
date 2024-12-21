# SignsOfLife (User Activity Monitor)

This project monitors user activity on a computer and sends email notifications when no user activity is detected for a 
specified period and also when user activity resumes. It tracks both keyboard and mouse events and triggers alerts accordingly.

This project is not designed for employee surveillance. Instead, it is intended as a passive health monitoring solution for
individuals who live alone and spend significant time on their PC. Inspired by the need to ensure the well-being of a remote-working
relative, it provides peace of mind by detecting inactivity and notifying friends or neighbours to check in, should something unexpected
have happened.

## Features
- Monitors user activity in real-time (keyboard and mouse).
- Sends email notifications if the user is inactive for a set duration (e.g. 1 hour).
- Sends email notifications whenever the user becomes active again ('waking' state).
- State management for tracking activity status (`active`, `inactive`, `waking`).
- Configurable inactivity check interval and email recipient.
- Can be easily customized to fit personal needs.

## How it Works
- The script continuously checks for user input (keyboard and mouse activity) during specified hours of the day (default: 9am-6pm).
- If no activity is detected for a specified duration (default: 1 hour), an email is sent.
- The system enters a "waking" state if activity is detected after being inactive and sends a "waking" notification.

## Setup
### 1. Clone this repository:
   ```
   git clone https://github.com/LaurenceMolloy/SignsOfLife.git
   ```
### 2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
### 3. Update the script with your email credentials:
   - Set your email address (`EMAIL_ADDRESS`) and password (`EMAIL_PASSWORD`).
   - Set the recipient's email (`RECIPIENT_EMAIL`).
### 4. (TESTING) Run the script:
   ```
   python signs_of_life.py
   ```
### 5. (PRODUCTION) Set up as a scheduled task or system service to run on startup:
   - Windows: Use Task Scheduler to run the script at startup.
   - Linux/macOS: Set up a cron job or use systemd to run the script automatically when the system starts.


# CICD

Combine_states.py runs every 30 minutes via CI/CD (see combine_states.yml in the .github/workflows folder). It aggregates heartbeats and statuses from all monitored devices, updates data/heartbeat.txt and data/state.txt, and sends email alerts for any changes, reporting lost/recovered communication with devices and user activity (the vital “signs of life” metric).

Testing shows the process takes about 20 seconds of CI/CD runner time per run. At 30-minute intervals, this amounts to roughly 500 minutes per month. With GitHub providing 2000 free CI/CD minutes monthly, this should comfortably fit within your free allowance - assuming light CI/CD usage elsewhere.

