import tkinter as tk
from cProfile import label
from tkinter import ttk, simpledialog
from PIL import Image, ImageTk
import pyautogui
import time as pytime
import pygetwindow as gw
import threading
import random
import json
import requests
import urllib.request
import urllib.error
import sys, os
from datetime import datetime, timezone, timedelta, date, time as dtime

from pathlib import Path
import sys

def resource_path(relative_path: str) -> str:
    """
    Load files relative to the EXE (when frozen) or this .py file (when running normally),
    regardless of where the script is launched from.
    """
    if getattr(sys, "frozen", False):
        # Running from EXE
        base_dir = Path(sys.executable).parent
    else:
        # Running from Python script
        base_dir = Path(__file__).parent
    return str(base_dir / relative_path)

# =========================
# CONFIG
# =========================

# Paste Alliance Discord webhook URL here (leave empty "" to disable alerts)
DISCORD_WEBHOOK_URL = ""

# If you prefer role mention instead of @everyone, put the ROLE ID here as a string (or leave None)
MENTION_ROLE_ID = None

# Alert cooldowns (seconds) to avoid spam - key word AVOID SPAM
DIG_ALERT_COOLDOWN_SECONDS = 1800
DRONE_ALERT_COOLDOWN_SECONDS = 1800

# PyAutoGUI image match confidence
CONFIDENCE = 0.7

# -------------------------
# Arms Race schedule look up
# Server time = GMT-2
# -------------------------

AR_SLOTS = [
    dtime(0, 0),
    dtime(4, 0),
    dtime(8, 0),
    dtime(12, 0),
    dtime(16, 0),
    dtime(20, 0),
]

# 7-day repeating schedule (Day 1..7)
# Index 0 = Day 1
AR_SCHEDULE = [
    # Day 1 Drone
    [
        'Base Building',
        'Unit Progression',
        'Hero Advancement',
        'Tech Research',
        'Drone Boost',
        'Hero Advancement',
    ],
    # Day 2 Build
    [
        'Unit Progression',
        'Tech Research',
        'Base Building',
        'Drone Boost',
        'Hero Advancement',
        'Base Building',
    ],
    # Day 3 Tech
    [
        'Drone Boost',
        'Hero Advancement',
        'Tech Research',
        'Base Building',
        'Unit Progression',
        'Tech Research',
    ],
    # Day 4 Hero
    [
        'Base Building',
        'Unit Progression',
        'Hero Advancement',
        'Tech Research',
        'Drone Boost',
        'Hero Advancement',
    ],
    # Day 5 Troop building
    [
        'Tech Research',
        'Drone Boost',
        'Unit Progression',
        'Hero Advancement',
        'Base Building',
        'Unit Progression',
    ],
    # Day 6 Enemy Buster
    [
        'Unit Progression',
        'Tech Research',
        'Base Building',
        'Drone Boost',
        'Hero Advancement',
        'Base Building',
    ],
    # Day 7 Frontline Breakthrough
    [
        'Drone Boost',
        'Hero Advancement',
        'Tech Research',
        'Base Building',
        'Unit Progression',
        'Tech Research',
    ],
]

# --- Arms Race colors (GUI styling) ---
COLOR_PREFIX  = "#000000"  # black for the words "Current:" and "Up next:"
COLOR_CURRENT = "#d32f2f"  # red (bold) for current event name
COLOR_NEXT    = "#1976d2"  # blue for up next event name

# =========================
# GLOBAL STATE
# =========================
current_res = '1720X1080' # changing resolution would need fresh screen shots to match 
game_screen_x, game_screen_y = map(int, current_res.split('X'))
max_search_area = (0, 0, game_screen_x + 50, game_screen_y + 50)
paused = False
running = True

# Session counters
help_count = 0
rally_count = 0
dig_count = 0
drone_count = 0
ALL_TIME_FILE = 'rally_bot_all_time_stats.json'

_last_dig_alert_ts = 0.0
_last_drone_alert_ts = 0.0

# GUI-level toggles
alert_digs_var = None
alert_drone_var = None

# Tk StringVars for dynamic UI
server_time_var = None
ar_current_var = None
ar_next_var = None
ar_countdown_var = None  # countdown to next slot


# =========================
# IMAGE PATHS
# =========================

#logo

logo_path_path  = resource_path('rally_bot_images/XDLogo.png')

#general use 
help_button_path  = resource_path('rally_bot_images/help_button.png')
back_button_path  = resource_path('rally_bot_images/back_button.png')

#rally flow
rally_button_path  = resource_path('rally_bot_images/rallies_button.png')
join_rally_button_path  = resource_path('rally_bot_images/join_rally_button.png')
zombie_boss_icon_path = resource_path('rally_bot_images/zombie_boss_icon.png' ) # Boss icon filter
march_button_path  = resource_path('rally_bot_images/march_button.png')

# Unit status icons (mean FREE / AVAILABLE units)
returning_unit_path  = resource_path('rally_bot_images/return_unit_status.png')  # return
idle_unit_path  = resource_path('rally_bot_images/idle_unit_status.png' )   # idle

# Dig flow
dig_alert_path  = resource_path('rally_bot_images/dig_alert.png')
dig_up_treasure_path = resource_path('rally_bot_images/dig_up_treasure.png')
chose_dig_path = resource_path('rally_bot_images/select_dig.png')
excavator_path = resource_path('rally_bot_images/dig_main.png')
join_dig_path = resource_path('rally_bot_images/join_dig.png')
gift__path = resource_path('rally_bot_images/gift.png')

# Drone flow 
drone_alert_path = resource_path('rally_bot_images/drone_alert.png')
tff_path = resource_path('rally_bot_images/test_flight_failure.png')
drone_path = resource_path('rally_bot_images/drone_main.png')
join_drone_path = resource_path('rally_bot_images/join_drone.png')
#img17a_path = resource_path('rally_bot_images/drone_clicktime_10.png')

# Other-device login detection + confirm button
currently_active_path = resource_path('rally_bot_images/currently_active.png')
red_confirm_path = resource_path('rally_bot_images/red_confirm.png')
# dont quit
cancel_path = resource_path('rally_bot_images/dontquit.png')

#accidental clicking escape and reorienting
reinforce_button_path = resource_path('rally_bot_images/reinforce_button.png')
base_path = resource_path('rally_bot_images/base.png')
world_path = resource_path('rally_bot_images/world.png')

#shields

shield_8_path = resource_path('rally_bot_images/8hr.png')
shield_12_path = resource_path('rally_bot_images/12hr.png')
shield_24_path = resource_path('rally_bot_images/24hr.png')
shield_button_path = resource_path('rally_bot_images/shield_button.png')
shield_use_button_path = resource_path('rally_bot_images/use_button.png')

# All-time (loaded) stats
_all_time_loaded = {"helps": 0, "rallies": 0, "digs": 0, "drone": 0}



def save_all_time_stats():
    totals = {
        "helps": _all_time_loaded["helps"] + help_count,
        "rallies": _all_time_loaded["rallies"] + rally_count,
        "digs": _all_time_loaded["digs"] + dig_count,
        "drone": _all_time_loaded["drone"] + drone_count,
    }
    try:
        with open(ALL_TIME_FILE, "w", encoding="utf-8") as f:
            json.dump(totals, f, indent=2)
    except Exception as e:
        print(f"Failed to save all-time stats: {e}")

# =========================
# TIME HELPERS (Server = GMT−2)
# =========================
def get_server_time() -> datetime:
    """
    Server time = UTC - 2h (GMT−2) all year round.
    Returns naive datetime in server-local representation.
    """
    return (datetime.now(timezone.utc) - timedelta(hours=2)).replace(tzinfo=None)

#==============
# Arms Race
#==============

def compute_arms_race_state(server_now: datetime):
    day_index = server_now.weekday()
    today = AR_SCHEDULE[day_index]

    current_slot = -1
    for i, t in enumerate(AR_SLOTS):
        if server_now < datetime.combine(server_now.date(), t):
            current_slot = i - 1
            break
    else:
        current_slot = len(AR_SLOTS) - 1

    if current_slot < 0:
        current_event = AR_SCHEDULE[(day_index - 1) % 7][-1]
    else:
        current_event = today[current_slot]

    next_slot = current_slot + 1
    if next_slot < len(AR_SLOTS):
        next_event = today[next_slot]
        next_dt = datetime.combine(server_now.date(), AR_SLOTS[next_slot])
    else:
        next_event = AR_SCHEDULE[(day_index + 1) % 7][0]
        next_dt = datetime.combine(server_now.date() + timedelta(days=1), AR_SLOTS[0])

    seconds_to_next_slot = int((next_dt - server_now).total_seconds())

    seconds_to_unit = None
    for i in range(current_slot + 1, len(AR_SLOTS)):
        if today[i] == "Unit Progression":
            dt = datetime.combine(server_now.date(), AR_SLOTS[i])
            seconds_to_unit = int((dt - server_now).total_seconds())
            break

    if seconds_to_unit is None:
        for offset in range(1, 8):
            sched = AR_SCHEDULE[(day_index + offset) % 7]
            for i, ev in enumerate(sched):
                if ev == "Unit Progression":
                    dt = datetime.combine(
                        server_now.date() + timedelta(days=offset),
                        AR_SLOTS[i]
                    )
                    seconds_to_unit = int((dt - server_now).total_seconds())
                    break
            if seconds_to_unit is not None:
                break

    return current_event, next_event, seconds_to_next_slot, seconds_to_unit

def format_hms(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

# =========================
# WINDOW MANAGEMENT
# =========================
def resize_game_window(title="Last War-Survival Game"):
    try:

        windows = gw.getWindowsWithTitle(title)
        if windows:
            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.resizeTo(game_screen_x, game_screen_y)
            win.moveTo(0, 0)
            print(f"Resized and moved window: {title}")
        else:
            print(f"No window found with title containing '{title}'")

    except Exception as e:
        print(f"Could not resize window: {e}")

# =========================
# IMAGE & CLICK HELPERS
# =========================
def find_and_click(image_path, description, confidence=CONFIDENCE, region=max_search_area ):
    """Locate an image on screen and click its center (full screen search)."""
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence, region=region)
        if location:
            #print(f"Clicking on {description} at {location}")
            pyautogui.click(location)
            pytime.sleep(0.5)
            return True
        else:
            print(f"{description} not found.")
            return False
    except Exception:
        return False

def locate_one(image_path, region=None, confidence=CONFIDENCE):
    try:
        return pyautogui.locateOnScreen(image_path, region=region, confidence=confidence)
    except Exception:
        return None

def find_and_click_in_region(image_path, description, region, confidence=CONFIDENCE):
    try:
        center = pyautogui.locateCenterOnScreen(image_path, region=region, confidence=confidence)
        if center:
            #print(f"Clicking on {description} at {center} within region {region}")
            pyautogui.click(center)
            pytime.sleep(0.5)
            return True
        else:
            print(f"{description} not found in region {region}.")
            return False
    except Exception:
        return False

def expand_region_around_box(box, radius=200):
    """Return a (left, top, width, height) region centered on the given box center."""
    left, top, width, height = box.left, box.top, box.width, box.height
    cx = left + width // 2
    cy = top + height // 2
    region_left   = max(0, cx - radius)
    region_top    = max(0, cy - radius)
    region_width  = radius * 2
    region_height = radius * 2
    return (region_left, region_top, region_width, region_height)

def press_esc_twice():
    pyautogui.press('esc')
    pytime.sleep(1)
    
    try:            
        see_base = pyautogui.locateCenterOnScreen(base_path, confidence=CONFIDENCE)            
    except pyautogui.ImageNotFoundException:
        see_base = None
    if not see_base:
     pyautogui.press('esc')

# =========================
# DISCORD WEBHOOK ALERTS
# =========================

def _post_discord(content_text: str) -> bool:
    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook URL not set; skipping send.")
        return False

    
    content = content_text
    
    #optional
    if MENTION_ROLE_ID:
        content = f"<@&{MENTION_ROLE_ID}> {content_text}"

    payload = {
        "content": content,
        "allowed_mentions": (
            {"parse": []}
            if not MENTION_ROLE_ID
            else {"parse": [], "roles": [str(MENTION_ROLE_ID)]}
        ),
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; RallyBot/1.0)",
    }

    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        print(f"Discord webhook sent. HTTP {resp.status_code}")
        return resp.ok
    except requests.exceptions.RequestException as e:
        print(f"Discord webhook error: {e}")
        return False

def send_dig_detected_alert(event):
    """Fire a 'dig detected' alert with cooldown and session counters (if toggle enabled)."""
    global _last_dig_alert_ts
    if not DISCORD_WEBHOOK_URL or alert_digs_var is None or not alert_digs_var.get():
        return

    now = pytime.time()
    if now - _last_dig_alert_ts < DIG_ALERT_COOLDOWN_SECONDS:
        return  # cooldown active

    msg = (
        f"We have a {event}!.\n Log In!!"
        #f"Session — Helps: {help_count} | Rallies: {rally_count} | Digs: {dig_count} | Drone: {drone_count}"
    )
    ok = _post_discord(
        content_text=msg,
    )
    if ok:
        _last_dig_alert_ts = now

def send_custom_announcement(root):
    """Ask for a message and post to Discord (prefixes role if configured), pausing the bot while composing."""
    global paused

    # Pause while the modal dialog is open
    was_paused = paused
    paused = True
    try:
        if not DISCORD_WEBHOOK_URL:
            print("Discord webhook URL not set; cannot send custom announcement.")
            return
        text = simpledialog.askstring("Custom Announcement", "Enter announcement message:", parent=root)
        if not text:
            return

        _post_discord(content_text=text)
    finally:
        # Restore the previous pause state
        paused = was_paused

#======================
# Print Redirect
#======================

class PrintRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # auto-scroll

    def flush(self):
        pass


# =========================
# SHIELD LOGIC
# =========================
def finalise(search_region):
    try:
        print(f'finalising')
        find_and_click(cancel_path, 'cancel button')
        use_button = pyautogui.locateCenterOnScreen(shield_use_button_path, confidence=CONFIDENCE, region=search_region)
        pytime.sleep(1)
        
        if use_button:
            press_esc_twice()
    except Exception as e:
        print(e)
        return

def use_shield(duration):
    reorient_screen()
    pyautogui.sleep(1)
    pyautogui.click(game_screen_x / 2, game_screen_y / 2)
    pyautogui.sleep(0.5)
    find_and_click(shield_button_path, 'Shield Button')
    pyautogui.sleep(0.5)

    shield_choice = None
    try:
        shield_choice = pyautogui.locateCenterOnScreen(duration, confidence=CONFIDENCE, region=max_search_area)
    except Exception as e:
        print(f"Error locating image: {e}\nUse of {duration} shield failed")

    if shield_choice is None:
        print(f"Shield image {duration} not found. Trying fallback...")
        if find_and_click(shield_use_button_path, 'Shield Use Button'):
            print("Fallback: Shield activated without specific duration.")
            return
        else:
            print("Shield activation failed: No shield image or use button found.")
            return

    center_x, center_y = shield_choice
    search_region = (
        max(0, center_x + 200),
        max(0, center_y + 0),
        200,
        100
    )
    print(f' found the shield {shield_choice} looking for button')

    if find_and_click(shield_use_button_path, 'Shield Use Button', confidence=CONFIDENCE, region=search_region):
        print(f'{duration} shield used successfully.')
        finalise(search_region)
    #fallback if no shield in inventory for chosen shield
    elif find_and_click(shield_use_button_path, 'Shield Use Button', confidence=CONFIDENCE, region=max_search_area):
        print(f'{duration} shield used successfully.')
        finalise(search_region)

    else:
        #no shield available at all
        pyautogui.press('esc')
        print(f'Use of {duration} shield UNSUCCESSFUL. Please buy a shield')


# =========================
# MARCH LOGIC
# =========================
def attempt_march_with_status_logic(increment_counter: str = None):
    """
    logic:

    - If March button is visible -> click it (success).
    - Else, if RETURN or IDLE status icon is found => units are FREE:
        * Click the status icon.
        * Try to click March within ±200px of that icon.
        * If still not found, try full-screen March.
        * If still not found, ESC x2 and fail.
    - Else (no status icons at all) => units are BUSY:
        * ESC x2 and fail.

    increment_counter: "rally" or "dig" or "drone" or None
    Returns True if March clicked, else False.
    """
    global rally_count, dig_count, drone_count

    # 1) Direct attempt
    if find_and_click(march_button_path, 'March Button'):
        if increment_counter == "rally":
            rally_count += 1
        elif increment_counter == "dig":
            dig_count += 1
        elif increment_counter == "drone":
            drone_count += 1
        else: press_esc_twice()
        return True

    print("March not found. Checking unit statuses (return/idle => FREE)...")
    #look for idle units
    idle_box = locate_one(idle_unit_path, confidence=CONFIDENCE)
    
    if idle_box:
        status_box = idle_box
    
    else:
        # only use idle units
        if task_vars['unit_selection'].get() == 'idle only':
            print("No Idle Units Found.")
            press_esc_twice()
            return False
        
        #look for returning units
        ret_box = locate_one(returning_unit_path, confidence=CONFIDENCE)
        if not ret_box:
            #exit if no free unit isnt found
            print("All Squads are busy.")
            press_esc_twice()
            return False
        status_box = ret_box
    
    
        
    center = pyautogui.center(status_box)
    print(f"Clicking status {status_box} (FREE), attempting to March...")
    pyautogui.click(center)
    pytime.sleep(0.2)  # allow UI update

    # Try within ±200px first
    region = expand_region_around_box(status_box, radius=200)
    if find_and_click_in_region(march_button_path, 'March Button', region):
        pyautogui.press('esc') # prevents stuck between marches
        if increment_counter == "rally":
            rally_count += 1
        elif increment_counter == "dig":
            dig_count += 1
        elif increment_counter == "drone":
            drone_count += 1
        return True

    # Fallback: full-screen
    if find_and_click(march_button_path, 'March Button'):
        if increment_counter == "rally":
            rally_count += 1
        elif increment_counter == "dig":
            dig_count += 1
        elif increment_counter == "drone":
            drone_count += 1
        return True

    print("March still not found. ESC")
    pyautogui.press('esc')
    return False

#=========================
# Drag Screen
#=========================
'''
drags screen
helpful to escape from accidental hq clicks
'''
def drag_screen(x_offset=100, y_offset=100, duration=1):
    """
    Drags the mouse slightly from its current position.

    Parameters:

    """
    start_x, start_y = 500,250
    pyautogui.moveTo(start_x, start_y, duration=0.3)
    pyautogui.mouseDown()
    pyautogui.move(x_offset*random.choice([-1,1]), y_offset*random.choice([-1,1]), duration=duration)
    pyautogui.mouseUp(start_x + x_offset, start_y + y_offset, duration=duration)

# =========================
# AUTO SHIELD SYSTEM
# =========================

# Tkinter variables for Auto Shield
auto_shield_var = None
shield_duration_var = None

# Shield mapping
shield_map = {
    "8hr": shield_8_path,
    "12hr": shield_12_path,
    "24hr": shield_24_path
}

def schedule_auto_shield():
    while running:
        if auto_shield_var and auto_shield_var.get():
            now = get_server_time()
            # Calculate next Friday 23:59 server time
            days_until_friday = (4 - now.weekday()) % 7  # Friday = 4
            target_date = now.date() + timedelta(days=days_until_friday)
            target_time = datetime.combine(target_date, dtime(23, 59))
            wait_seconds = (target_time - now).total_seconds()
            if wait_seconds > 0:
                print(f"Auto Shield scheduled in {wait_seconds/3600:.2f} hours.")
                pytime.sleep(wait_seconds)
                selected = shield_duration_var.get()
                image_path = shield_map.get(selected)
                if image_path:
                    print(f"Activating auto shield: {selected}")
                    use_shield(image_path)
        pytime.sleep(60)  # Check every minute


# =========================
# TASKS
# =========================
def task0():
    """ Check for accidental ally HQ clicks (most common) - need a better solution as it could click other objects"""
    try:
        reinforce_button = pyautogui.locateCenterOnScreen(reinforce_button_path, confidence=0.8)
        if reinforce_button:
            #pyautogui.click(reinforce_button) #for debugging delete with the print statement when clear
            print(f'reinforce button found at {reinforce_button}')
            drag_screen()
            return
        #pytime.sleep(0.2)

    except Exception:
        return

def task1():
    """Tap Help."""
    if find_and_click(help_button_path, 'Help Button', confidence= 0.9):
        global help_count
        help_count += 1
        print(f"Help Button clicked. Total helps: {help_count}")

def task2():
    """Join Boss Rally (filtered by ZOMBIE BOSS img4) and attempt March."""
    if not find_and_click(rally_button_path, 'Rallies Button'):
        return

    pytime.sleep(0.2)

    try:
        matches_img4 = list(pyautogui.locateAllOnScreen(zombie_boss_icon_path, confidence=CONFIDENCE))
    except Exception as e:
        print(f"Error locating img4: {e}")
        find_and_click(back_button_path, 'Back Button')
        return

    if not matches_img4:
        print("No ZOMBIE BOSS rally found. Clicking Back.")
        find_and_click(back_button_path, 'Back Button')
        return
    sorted_img4 = sorted(matches_img4, key=lambda x: x.top)

    for img4_box in sorted_img4:
        print(f"Found ZOMBIE BOSS at {img4_box}")
        center_x, center_y = pyautogui.center(img4_box)
        search_region = (
            max(0, center_x - 200),
            max(0, center_y - 200),
            200,
            200
        )

        try:
            matches_img3 = list(pyautogui.locateAllOnScreen(join_rally_button_path, region=search_region, confidence=CONFIDENCE))
        except Exception as e:
            print(f"Error locating image: {e}")
            continue

        if matches_img3:
            target_img3 = matches_img3[0]
            center = pyautogui.center(target_img3)
            #print(f"Clicking Join Rally at {center}")
            print(f'Joining Rally')
            pyautogui.click(center)
            pytime.sleep(0.7)

            # Check if March screen appeared
            try:
                march_visible = pyautogui.locateOnScreen(march_button_path, confidence=CONFIDENCE)

            except Exception:
                march_visible = None

            if march_visible:
                if attempt_march_with_status_logic(increment_counter="rally"):
                    return
                else:                    
                    print("Unable to march.")
                    press_esc_twice()
                    return
            else:
                print("Join rally failed. Trying next boss...")
                continue
    print("No valid Boss Rally found. Attempting to exit.")
    if not find_and_click(back_button_path, 'Back Button'):
        print("Back button not found. Pressing ESC twice.")
        press_esc_twice()

#====================
# DIG
#====================

def task3():
    """Join Dig flow + click gift + optional Discord alert."""
    # If a dig alert is visible, send Discord (respect toggle/cooldown) and click it
    alert_box = locate_one(dig_alert_path, confidence=CONFIDENCE)
    alert_box_2 = locate_one(drone_alert_path, confidence=CONFIDENCE)
    
    if not alert_box and not alert_box_2:
        return
            
    if alert_box:
        alert, dig, loc, event, join = alert_box, dig_up_treasure_path, excavator_path, join_dig_path, 'dig'
    elif alert_box_2:
        alert, dig, loc, event, join = alert_box_2, tff_path, drone_path, join_drone_path, 'drone'
    else:
        return

    if alert:
        print(f"Found dig alert at {alert}.")
        send_dig_detected_alert(event)
        pyautogui.click(pyautogui.center(alert))
        pytime.sleep(0.7)

    # look for dig_up_treasure coordinates
    if not find_and_click(dig, 'Dig/Drone'):
        return
    
    pytime.sleep(0.7)
    # click dig_main body to join dig
    if not find_and_click(loc, 'event location'):
        print("Excavator/Drone not found. Exiting task3.")
        return

    pytime.sleep(0.7)

    try:
        #when dig is next to hq and a choice needs to be made which to click
        chose_dig = pyautogui.locateCenterOnScreen(chose_dig_path, confidence=CONFIDENCE, region = max_search_area)
        if chose_dig:
            print("Dig choice encoutered.")
            pyautogui.click(chose_dig) 
            pytime.sleep(0.7)
        else: return
    except Exception as e:
        print(f' this{e}')
    
   
    
    # join_dig
    if not find_and_click(join, 'Join Dig/Drone'):
        print("Join Dig button not found. Exiting task3.")
        return

    pytime.sleep(0.7)
    # March (increment dig counter on success)
    marched = attempt_march_with_status_logic(increment_counter="dig")
    if not marched:
        print("Dig: March not performed.")
        return
    
    ''' # dig logic/ clicking the gift

    start_time = pytime.time()
    timeout = 60  # exit plan in case gift was missed by pyautogui as it goes too fast sometimes
    pytime.sleep(10)
    while True: # while excavator is visible
        pyautogui.locateCenterOnScreen(event, confidence=CONFIDENCE)
        try:
           

            if pytime.time() - start_time > timeout: #fall back plan
                print("Timed out waiting for gift.")
                break

             # check for gift icon
            gift = pyautogui.locateCenterOnScreen(gift__path, confidence=CONFIDENCE)
            if gift: #when gift appears
                pyautogui.click(gift) # click it
                print("Gift clicked.")
                break
            else: # excavator visible no gift
                print("Waiting for gift to appear...")
                pytime.sleep(0.5)
        except Exception as e:
            print(e)
            return
    '''
def detect_and_terminate_if_other_login(root, show_status_fn):
    global running
    notice = locate_one(currently_active_path, confidence=CONFIDENCE)
    if notice:
        print(f"Detected other-device login notice at {notice}.")
        clicked = find_and_click(red_confirm_path, 'Confirm/OK after other-device login', confidence=CONFIDENCE)
        if not clicked:
            print("Confirm/OK image (img19_path) not found; exiting anyway.")
        try:
            if show_status_fn:
                show_status_fn("Another device login detected — exiting", "error")
        except Exception:
            pass
        save_all_time_stats()
        running = False
        try:
            if root:
                print(f'Attempting to Exit')
                pytime.sleep(1)
                root.destroy()
        except Exception:
            print(f"Error destroying root: {e}")
        return True
    return False


def click_if_dont_quit():
    if find_and_click(cancel_path, 'Dont Quit Button'):
        print("Clicked Dont Quit button.")

def recentre_hq(world,base):
    if base:
        pyautogui.click(base)
        pyautogui.sleep(1)
        print(" x ")
    
    pyautogui.click(world)
    pyautogui.sleep(1)


def reorient_screen():
    try:
        base = pyautogui.locateCenterOnScreen(base_path, confidence=CONFIDENCE)
    except:
        base = None
    try:
        world = pyautogui.locateCenterOnScreen(world_path, confidence=CONFIDENCE)
    except:
        world = None

    if base == None and world == None:
        print(f'Don\'t panic')
        print("Reorienting view")
        pyautogui.press('esc')
        pyautogui.sleep(0.5)
        recentre_hq(world,base)

# =========================
# LOOP & GUI
# =========================
def run_selected_tasks(task_vars, root):
    global paused, running
    while running:
  
        if paused:
            pytime.sleep(0.5)
            continue            

        # Check for other-device login and terminate if needed
        if detect_and_terminate_if_other_login(root, show_status_fn = None):
            break

        # Click 'Don't Quit' if detected
        click_if_dont_quit()

        if task_vars['task1'].get():
            task1()
        if task_vars['task2'].get():            
            task2()
            pytime.sleep(0.5)
            reorient_screen()
        if task_vars['task3'].get():
            task3()
       # if not task_vars['task3'].get():
          #  announce_dig()
        if task_vars['task1'].get() or task_vars['task2'].get():
            task0()

            reorient_screen()
        
        pytime.sleep(0.5)  # Delay between task cycles

def toggle_pause(pause_button):
    global paused
    paused = not paused
    pause_button.config(text="Resume" if paused else "Pause")
    print("Paused." if paused else "Resumed.")

def update_time_and_arms_race(root):
    global server_time_var, ar_current_var, ar_next_var, ar_countdown_var, ar_unit_timer_var, ar_unit_timer_var
    try:
        server_now = get_server_time()
        server_time_var.set(f"Server time (GMT-2): {server_now.strftime('%H:%M:%S')}")
        current_event, next_event, secs_left, secs_unit = compute_arms_race_state(server_now)
        ar_current_var.set(current_event)
        ar_next_var.set(next_event)
        ar_countdown_var.set(f"Next in: {format_hms(secs_left)}")
        ar_unit_timer_var.set(format_hms(secs_unit))
    except Exception as e:
        server_time_var.set("Server time: --:--:-- (err)")
        ar_current_var.set("—")
        ar_next_var.set("—")
        ar_countdown_var.set("Next in: —")
        ar_unit_timer_var.set("—")
        print(f"Time/Arms Race update error: {e}")
    root.after(1000, lambda: update_time_and_arms_race(root))


def start_gui():
    global running, alert_digs_var, alert_drone_var
    global server_time_var, ar_current_var, ar_next_var, ar_countdown_var, ar_unit_timer_var
    global auto_shield_var, shield_duration_var

    root = tk.Tk()
    root.title("XderBot Control Panel")

    try:
        root.geometry("+1721+0")
        root.attributes("-topmost", True)
    except Exception:
        pass

    
    # Start auto shield thread
    threading.Thread(target=schedule_auto_shield, daemon=True).start()

    global running, alert_digs_var, alert_drone_var, task_vars
    global server_time_var, ar_current_var, ar_next_var, ar_countdown_var, ar_unit_timer_var

    # Spawn top-most at x=1721, y=0 
    try:
        root.geometry("+1721+0")
        root.attributes("-topmost", True)
    except Exception:
        pass

    # ===== Top header frame with Left (Arms Race) and Right (Logo) =====
    header = tk.Frame(root)
    header.pack(fill='x', padx=10, pady=(8, 6))

    # LEFT: Arms Race panel
    left_panel = ttk.LabelFrame(header, text="Arms Race")
    left_panel.pack(side='left', fill='x', expand=True, padx=(0, 10))

    server_time_var = tk.StringVar(value="Server time (GMT-2): --:--:--")
    ar_current_var  = tk.StringVar(value="—")   # just event name
    ar_next_var     = tk.StringVar(value="—")   # just event name
    ar_countdown_var = tk.StringVar(value="Next in: —")

    
    ar_unit_timer_var = tk.StringVar(value="—")  # countdown to Unit Progression

    ttk.Label(left_panel, textvariable=server_time_var, font=("Segoe UI", 10, "bold")).pack(
        anchor='w', padx=8, pady=(6, 2)
    )

    # Current row
    cur_row = tk.Frame(left_panel)
    cur_row.pack(anchor='w', padx=8, pady=1, fill='x')
    tk.Label(cur_row, text="Current: ", font=("Segoe UI", 10), fg=COLOR_PREFIX).pack(side='left')
    tk.Label(cur_row, textvariable=ar_current_var, font=("Segoe UI", 10, "bold"), fg=COLOR_CURRENT).pack(side='left')

    # Up next row
    next_row = tk.Frame(left_panel)
    next_row.pack(anchor='w', padx=8, pady=1, fill='x')
    tk.Label(next_row, text="Up next: ", font=("Segoe UI", 10), fg=COLOR_PREFIX).pack(side='left')
    tk.Label(next_row, textvariable=ar_next_var, font=("Segoe UI", 10), fg=COLOR_NEXT).pack(side='left')

    # Troop Training row
    troop_row = tk.Frame(left_panel)
    troop_row.pack(anchor='w', padx=8, pady=1, fill='x')
    tk.Label(troop_row, text="Troop Training in: ", font=("Segoe UI", 10), fg=COLOR_PREFIX).pack(side='left')
    tk.Label(troop_row, textvariable=ar_unit_timer_var, font=("Segoe UI", 10), fg="#008000").pack(side='left')

    # RIGHT: Logo
    right_panel = tk.Frame(header)
    right_panel.pack(side='right', anchor='ne')

    try:

        logo_img = Image.open(logo_path_path)
        logo_img = logo_img.resize((120, 115), Image.LANCZOS)
        logo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(right_panel, image=logo)
        logo_label.image = logo
        logo_label.pack()
        awesomeness_label = tk.Label(right_panel, text="AWESOMENESS", font=("Segoe UI", 12, "bold"))
        awesomeness_label.pack()

    except Exception as e:
        print(f"Error loading logo: {e}")



    # ===== Tasks and toggles =====
    
    tasks_frame = ttk.LabelFrame(root, text="Select Tasks")
    tasks_frame.pack(padx=10, pady=6, fill='x')

    # Split into two columns
    left_tasks = tk.Frame(tasks_frame)
    left_tasks.pack(side='left', fill='both', expand=True, padx=(8, 4))

    right_shield = tk.Frame(tasks_frame)
    right_shield.pack(side='right', fill='both', expand=True, padx=(4, 8))

    # Left column: Task checkboxes
    task_vars = {
        'task1': tk.BooleanVar(value=False),  # Tap Help
        'task2': tk.BooleanVar(value=False),  # Join Boss Rally
        'unit_selection' : tk.StringVar(value='idle'), #Idle Troops
        'task3': tk.BooleanVar(value=False),  # Join Dig / Drone
    }

    ttk.Checkbutton(left_tasks, text="Tap Help", variable=task_vars['task1']).pack(anchor='w', pady=2)
    ttk.Checkbutton(left_tasks, text="Join Boss Rally", variable=task_vars['task2']).pack(anchor='w', pady=2)
    ttk.Radiobutton(left_tasks, text="Idle Only", variable=task_vars['unit_selection'], value="idle").pack(anchor='w', pady=2, padx=8)
    ttk.Radiobutton(left_tasks, text="Include Returning", variable=task_vars['unit_selection'], value="both").pack(anchor='w', pady=2, padx=8)
    ttk.Checkbutton(left_tasks, text="Join Dig", variable=task_vars['task3']).pack(anchor='w', pady=2)

    # Announcement toggles
    alert_digs_var = tk.BooleanVar(value=False)
    alert_drone_var = tk.BooleanVar(value=False)
    #ttk.Checkbutton(left_tasks, text="Announce Digs (Discord)", variable=alert_digs_var).pack(anchor='w', pady=(6, 2))
    #ttk.Checkbutton(left_tasks, text="Announce Drones (Discord)", variable=alert_drone_var).pack(anchor='w', pady=(0, 6))

    # Right column: Auto Shield controls
    auto_shield_var = tk.BooleanVar(value=False)
    shield_duration_var = tk.StringVar(value="24hr")

    ttk.Checkbutton(right_shield, text="Enable Auto Shield", variable=auto_shield_var).pack(anchor='w', pady=(0, 4))
    ttk.Label(right_shield, text="Shield Duration:").pack(anchor='w')
    ttk.Combobox(right_shield, textvariable=shield_duration_var, values=["8hr", "12hr", "24hr"], state="readonly").pack(anchor='w', pady=(2, 6))

    # TESTING button
    ttk.Button(right_shield, text="Use Shield", command=lambda: use_shield(shield_map.get(shield_duration_var.get()))).pack(anchor='w', padx=12, pady=(0, 6))


    # ===== Buttons (Run Task) =====
    button_frame = tk.Frame(root)
    button_frame.pack(pady=6)

    resize_button = ttk.Button(button_frame, text="Resize Window", command=resize_game_window)
    resize_button.grid(row=0, column=0, padx=5)

    pause_button = ttk.Button(button_frame, text="Pause", command=lambda: toggle_pause(pause_button))
    pause_button.grid(row=0, column=1, padx=5)

    announce_button = ttk.Button(button_frame, text="Custom Announcement", command=lambda: send_custom_announcement(root))
    announce_button.grid(row=0, column=2, padx=5)

    #====== Status ======
    
    log_text = tk.Text(root, height=5, width=45)
    log_text.pack(padx=10, pady=10)

    
    sys.stdout = PrintRedirector(log_text)
    sys.stderr = PrintRedirector(log_text)



    # ===== Stats line =====
    stats_var = tk.StringVar(value="Helps: 0 | Rallies: 0 | Digs: 0 | Drone: 0")
    stats_label = ttk.Label(root, textvariable=stats_var, font=("Segoe UI", 10))
    stats_label.pack(pady=(0, 10))

    def refresh_stats():
        stats_var.set(f"Helps: {help_count} | Rallies: {rally_count} | Digs: {dig_count} | Drone: {drone_count}")
        root.after(500, refresh_stats)

    refresh_stats()

    # Start periodic time & arms race updater
    #global server_time_var, ar_current_var, ar_next_var, ar_countdown_var, ar_unit_timer_var, ar_unit_timer_var
    update_time_and_arms_race(root)

    # Start tasks automatically (no Run button)
    threading.Thread(target=run_selected_tasks, args=(task_vars, root), daemon=True).start()

    # shutdown on close
    def on_close():
        global running
        running = False
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

# ===== Entry point =====
if __name__ == "__main__":
    resize_game_window(title="Last War-Survival Game")
    start_gui()
    