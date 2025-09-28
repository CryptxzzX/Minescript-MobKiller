import math
import time
import threading
import smoothcam
from system.lib import minescript
from system.lib.minescript import echo_json, EventQueue, EventType
import types

TARGET_MOBS = ["sheep"]
KEY = types.SimpleNamespace()
KEY.TOGGLE = 75    # K
KEY.STOP = 61      # -

toggle_event = threading.Event()
stop_event = threading.Event()
target_lock = threading.Lock()
current_target = None
ATTACK_COOLDOWN = 0.5
SCAN_INTERVAL = 0.2
ATTACK_RADIUS = 4.0
def distance(a, b):
    return math.sqrt(sum((a[i] - b[i])**2 for i in range(3)))

def scan_targets(radius=ATTACK_RADIUS):
    while not stop_event.is_set():
        px, py, pz = minescript.player_position()
        candidates = []
        for entity in minescript.entities():
            if any(target in entity.name.lower() for target in TARGET_MOBS):
                ex, ey, ez = entity.position
                if distance((px, py, pz), (ex, ey, ez)) <= radius:
                    candidates.append(entity)

        with target_lock:
            global current_target
            current_target = min(candidates, key=lambda e: distance((px, py, pz), e.position)) if candidates else None

        time.sleep(SCAN_INTERVAL)

def mob_killer_loop():
    last_attack_time = 0
    while not stop_event.is_set():
        if toggle_event.is_set():
            with target_lock:
                target = current_target

            if target:
                tx, ty, tz = target.position
                smoothcam.lookat_tick(tx, ty, tz, factor=0.3)

                now = time.time()
                if now - last_attack_time >= ATTACK_COOLDOWN:
                    minescript.player_press_attack(True)
                    time.sleep(0.05)
                    minescript.player_press_attack(False)
                    last_attack_time = now
            else:
                echo_json('[{"text":"No targets nearby.", "color":"red"}]')
        time.sleep(0.05)
def event_listener():
    echo_json('[{"text":"Kill Mobs Service loaded. Press [K] to toggle.", "color":"blue"}]')
    with EventQueue() as event_queue:
        event_queue.register_key_listener()
        while not stop_event.is_set():
            event = event_queue.get()
            if event.type == EventType.KEY and event.action == 0:
                match event.key:
                    case KEY.TOGGLE:
                        if toggle_event.is_set():
                            toggle_event.clear()
                            echo_json('[{"text":"Mob Killing ", "color":"white"}, {"text":"OFF", "color":"red"}]')
                            minescript.player_press_attack(False)
                        else:
                            toggle_event.set()
                            echo_json('[{"text":"Mob Killing ", "color":"white"}, {"text":"ON", "color":"green"}]')
                    case KEY.STOP:
                        echo_json('[{"text":"Stopping Mob Killing Service...", "color":"blue"}]')
                        minescript.player_press_attack(False)
                        stop_event.set()

# Launch threads
threads = [
    threading.Thread(target=scan_targets, daemon=True),
    threading.Thread(target=mob_killer_loop, daemon=True),
    threading.Thread(target=event_listener)
]

for t in threads:
    t.start()

threads[-1].join()  # Wait for event_listener to finish