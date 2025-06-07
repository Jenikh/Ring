import os
import requests
import time
from urllib import request
import pygame  # For cross-platform sound
from datetime import datetime, timedelta, timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests
f_narozeniny = requests.get("https://jenikh.github.io/Ring/Narozeniny.mp3")
f_vanoce = requests.get("https://jenikh.github.io/Ring/Vanoce.mp3")
# Google Calendar API scopes
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
class update:
    def update(self):
        upd = requests.get("https://jenikh.github.io/Ring/update.py")
        with open("update.py", "w") as fi: fi.write(upd.text)
        os.system(f"py update.py")
        while not os.path.exists("state.txt"):
            time.sleep(1)
        with open("state.txt", "r") as fi: state = fi.read()
        os.remove("state.txt")
        if state == "Update":
            os.system(f"py update.py Can_Be_Updated")
            exit(1)
        return
# List of days with no calendar events (will be filled dynamically)
zvoneni_dny = []

# Initialize pygame for sound
pygame.mixer.init()

def play_sound():
    """Plays a short bell sound."""
    today = datetime.now().date()
    if today == datetime.date(datetime.now().year, 5, 19):
        # Play a different sound on May 19
        
        with open("ss.mp3", "wb") as fi:
            fi.write(f_narozeniny.content)
        time_s = 5
        
        pygame.mixer.music.load("ss.mp3")
    elif today <= datetime.date(datetime.now().year, 12, 0) and today >= datetime.date(datetime.now().year, 12, 24):
        
        with open("ss.mp3", "wb") as fi:
            fi.write(f_vanoce.content)
        
        pygame.mixer.music.load("ss.mp3")
    else:
        if os.path.exists("ss.mp3"):
            os.remove("ss.mp3")
        time_s = 2
        pygame.mixer.music.load("bell_sound.mp3")  # Replace with a real bell sound file
    pygame.mixer.music.play()
    time.sleep(time_s)  # Wait for sound to finish playing

def authenticate_google_calendar():
    """Authenticate and return the Google Calendar API service."""
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return build("calendar", "v3", credentials=creds)

def is_day_empty(service, calendar_id="primary", date=None):
    """Check if a given day has no events."""
    if date is None:
        date = datetime.now(timezone.utc).date()  # Default to today

    start_of_day = datetime.combine(date, datetime.min.time(), timezone.utc).isoformat()
    end_of_day = datetime.combine(date, datetime.max.time(), timezone.utc).isoformat()

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_of_day,
        timeMax=end_of_day,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    return len(events) == 0  # True if no events, False otherwise

def ring_bell():
    """Handles ringing schedule on a free day."""
    print("🔔 School Bell System Started! 🔔")

    # Define ringing times (in hours and minutes)
    ring_times = [
        (7, 10), (7, 25), (7, 30),  # Morning bells
        (8, 15), (8, 25),            # Period 1, 2
        (9, 10), (9, 25), (9, 30),          # Long break
        (10, 15), (10, 25),         # Period 3, 4
        (11, 10), (11, 20),         # Period 5, 6
        (12, 5), (12, 15),
        (13,0), (13,5), (13,50), # Period 7, 8 (max 8 hours)
        (13,55),(14,40)
    ]

    while True:
        now = datetime.now()
        old_now_minute = now.minute
        for ring_hour, ring_minute in ring_times:
            ring_time = now.replace(hour=ring_hour, minute=ring_minute, second=0, microsecond=0)

            if now < ring_time:  # If the ring time is in the future
                time_to_wait = (ring_time - now).total_seconds()
                print(f"🔔 Next bell at {ring_time.strftime('%H:%M')} (Waiting {time_to_wait // 60:.0f} min)")
                
                while now < ring_time:  # Wait until the ring time
                    time.sleep(1)
                    now = datetime.now()
                    
                    time_to_wait = (ring_time - now).total_seconds()
                    time_to_wait = time_to_wait // 60
                    if time_to_wait != old_now_minute:
                        print("Now waiting " + str(time_to_wait) + " min")
                        old_now_minute = time_to_wait
                        
                
                time.sleep(time_to_wait)  # Wait until ring time
                play_sound()
                print(f"🔔 Bell rang at {ring_time.strftime('%H:%M')}!")

        # Check if the school day is over (last ring at 13:55)
        if now.hour >= ring_times[len(ring_times) -1][1]:
            print("📅 School day ended. Exiting bell system.")
            
            break

if __name__ == "__main__":
    print("Want to load your own schedule? (y/n)")
    if input() == "y":
        own = True
        file = input("Enter file name: ")
        while not os.path.exists(file) or file.split(".")[1] != "txt":
            if not os.path.exists(file) or file.split(".")[1] != "txt":
                print("File does not exist or is not a .txt file.")
            file = input("Enter file name: ")
        
        with open(file, "r") as f:
            lines = f.readlines()
            for line in lines:
                try:
                    list(line)
                except:
                    continue
                ring_times = list(line)
                break
    else:
        own = False
    # Authenticate with Google Calendar
    service = authenticate_google_calendar()
    
    # Set your calendar ID
    calendar_id = "6cd023af9b6e0e7a9f543820fa9e0dab40b274abf5821a44cefbfb2345c9513c@group.calendar.google.com"
    check_date = datetime.now(timezone.utc).date()  # Start from today
    if not own:
        # Check for free days
        
        for _ in range(365):  # Loop for 30 days
            if is_day_empty(service, calendar_id, date=check_date):
                print(f"{check_date} is free (None).")
                zvoneni_dny.append(check_date)  # Add free days to the list

            check_date += timedelta(days=1)  # Move to the next day
    
    # If today is a free day, start the ringing schedule
    own = False
    while True:
        today = datetime.now().date()
        if today in zvoneni_dny:
            print(f"🔔 {today} is a free day, ringing the school bell schedule! 🔔")
            ring_bell()
            print("📅 Waiting for 24 hours before checking again.")
            a = 24
            while not time.time() >= (time.time() + 24 * 60 * 60):
                print(f"Waiting for {a} hours.")
                time.sleep(60 * 60)
                a -= 1
        else:
            print(f"📅 {today} has scheduled events. No ringing today.")
            print("📅 Waiting for 24 hours before checking again.")
            a = 24
            while not time.time() >= time.time() + 24 * 60 * 60:
                print(f"Waiting for {a} hours.")
                time.sleep(60 * 60)
                a -= 1
        
        for _ in range(30):  # Loop for 30 days
            if is_day_empty(service, calendar_id, date=check_date):
                print(f"{check_date} is free (None) — Added to zvoneni_dny.")
                zvoneni_dny.append(check_date)  # Add free days to the list
            else:
                print(f"{check_date} has scheduled events.")

            check_date += timedelta(days=1)  # Move to the next day
