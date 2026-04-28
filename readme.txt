**XderBot**

XderBot is a long‑running Python automation project built to assist with repetitive in‑game actions through visual GUI automation.
The project has undergone multiple major updates over more than a year, adapting to changing game interfaces and workflows.
This repository represents a real-world, production‑used automation tool, not a tutorial script.

**Overview**
XderBot automates selected in‑game actions by:

Observing the screen using image recognition
Identifying UI elements via stored reference images
Simulating mouse and keyboard input
Reacting to game state changes in real time
Providing runtime status, counters, and alerts via a custom GUI

The bot is state-aware but UI-driven, meaning all logic is derived from visible game elements rather than internal APIs.

**Key Features:**

Image-based automation

Uses confidence-based screen matching (pyautogui.locateOnScreen)
Region-constrained searches for performance and stability



**Modular task system**

Independent tasks (helping, rallies, digs, drones, shielding)
Central execution loop with pause/resume support


**GUI control panel (Tkinter)**

Live server-time display
Current and upcoming event tracking
Toggleable automation features
Session counters and status messages



**Arms Race schedule + Troop training countdown timer**

Server-time–adjusted event scheduling
Countdown logic for event transitions
Countdown logic in between Troop training events

**Tap Help**

Taps the help button when it pops up 


**Join Boss Rally**

Join Zombie boss rallies when there are space available

** Join Dig **

Joins Dig and clicks the gift icon. - work in progress.

**Safety & recovery logic**

Detection of forced logouts / other-device login prompts
“Don’t quit” and confirmation dialog handling
Screen re‑centering and orientation recovery



**Discord integration (optional)**

Custom Announcement
Webhook alerts for selected events
Cooldown logic to avoid alert spam



**Persistent statistics**

Session and all‑time counters saved to disk

Requirements

Python 3.9+
Windows (primary development target)
Dependencies:

pyautogui
pygetwindow
Pillow
tkinter (bundled with Python)
Optional: requests (Discord webhook alerts)


Install dependencies with:
pip install pyautogui pygetwindow pillow requests

**Legal & Ethical Notice**
This project is provided for educational and personal automation purposes only.

The author does not encourage violating any game’s Terms of Service
Users are responsible for ensuring their use complies with applicable rules
No guarantees are provided regarding safety, compatibility, or longevity