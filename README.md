# Minescript MobKiller

[![Status: Archived](https://img.shields.io/badge/status-archived-red.svg)](https://github.com/)

> **Notice:** This repository is **unmaintained and deprecated**. It is no longer in active development and will not receive bug fixes, updates, or compatibility patches. Feel free to fork and modify the codebase for your own use.

---

## Overview

Minescript MobKiller is an automated target-acquisition and combat script built for Minescript. It scans your surroundings within a defined radius, matches entities against a target list, and rotates the camera smoothly to engage them while managing attack cooldowns in a background thread.

### How It Works & How It's Used

1. **Setup:** Place `mobkiller.py` alongside `smoothcam.py` in your Minescript directory.
2. **Configuration:** Define your target mob names in the script's target array and adjust scan parameters to your preferences.
3. **Execution:** Launch the script via your Minescript keybind or console. Use the configured toggle key to start/pause combat routines and the stop key to cleanly terminate the script.

### Features

* **Target Filtering:** Automatically detects and filters targets by entity name using a custom target array.
* **Adjustable Attack Radius (`ATTACK_RADIUS`):** Restricts mob detection and targeting to a specified block distance.
* **Adjustable Attack Cooldown (`ATTACK_COOLDOWN`):** Tunes hit cadence to align with weapon attack speeds or server tick delays.
* **Adjustable Scan Interval (`SCAN_INTERVAL`):** Controls the frequency of entity sweeps to balance responsiveness and performance.
* **Configurable Keybinds (`TOGGLE` & `STOP`):** Quick-access controls for toggling the kill loop or killing the script immediately.
* **Multithreaded Architecture:** Runs scanning, aim smoothing, and attack routines concurrently for stutter-free gameplay.

---

# Requirements:
### YOU MUST HAVE SMOOTHCAM.PY WITH MOBKILLER.PY
