import math
import time
import threading
import smoothcam
from system.lib import minescript
from system.lib.minescript import echo_json, EventQueue, EventType
import types

# === Entity Types ===
class Entity:
    sheep = "minecraft.sheep"
    cow = "minecraft.cow"
    pig = "minecraft.pig"
    chicken = "minecraft.chicken"
    zombie = "minecraft.zombie"
    skeleton = "minecraft.skeleton"
    armour_stand = "minecraft.armor_stand"

# === Config ===
TARGET_MOBS = [Entity.sheep, Entity.cow, Entity.pig, Entity.chicken,
               Entity.zombie, Entity.skeleton]
IGNORE_ENTITIES = [Entity.armour_stand]

KEY = types.SimpleNamespace()
KEY.TOGGLE = 75    # K
KEY.STOP = 61      # -
ATTACK_RADIUS = 4.0
ATTACK_COOLDOWN = 0.5
SCAN_INTERVAL = 0.2
AIM_OFFSET_Y = 0.0

# === State ===
toggle_event = threading.Event()
stop_event = threading.Event()
target_lock = threading.Lock()
target_type = None
target_position = None

# === Utilities ===
def distance(a, b):
    return math.sqrt(sum((a[i] - b[i])**2 for i in range(3)))

# === Target Scanner ===
def scan_targets():
    global target_type, target_position
    while not stop_event.is_set():
        px, py, pz = minescript.player_position()

        with target_lock:
            # Validate current target
            entities = minescript.entities()
            if target_type and target_position:
                for e in entities:
                    if e.type != target_type:
                        continue

                    dist_to_last = distance(e.position, target_position)
                    dist_to_player = distance(e.position, (px, py, pz))

                    if dist_to_last < 1.5 and dist_to_player <= ATTACK_RADIUS:
                        target_position = e.position
                        break
                else:
                    target_type = None
                    target_position = None

            # Acquire new target
            if not target_type:
                candidates = []
                for e in entities:
                    type = e.type
                    if any(mob in type for mob in TARGET_MOBS) and not any(ignore in type for ignore in IGNORE_ENTITIES):
                        dist = distance(e.position, (px, py, pz))
                        if dist <= ATTACK_RADIUS:
                            candidates.append((e, dist))

                if candidates:
                    best, _ = min(candidates, key=lambda pair: pair[1])
                    target_type = best.type
                    target_position = best.position

        time.sleep(SCAN_INTERVAL)

# === Mob Killer ===
def mob_killer_loop():
    last_attack_time = 0
    while not stop_event.is_set():
        if toggle_event.is_set():
            with target_lock:
                if target_type and target_position:
                    tx, ty, tz = target_position
                    smoothcam.lookat_tick(tx, ty + AIM_OFFSET_Y, tz, 0.3)

                    now = time.time()
                    if now - last_attack_time >= ATTACK_COOLDOWN:
                        minescript.player_press_attack(True)
                        time.sleep(0.05)
                        minescript.player_press_attack(False)
                        last_attack_time = now

                    smoothcam.lookat_tick(tx, ty + AIM_OFFSET_Y, tz, 0.3)
                else:
                    time.sleep(0.1)
        time.sleep(0.05)

# === Key Listener ===
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


# === Launch Threads ===
threads = [
    threading.Thread(target=scan_targets, daemon=True),
    threading.Thread(target=mob_killer_loop, daemon=True),
    threading.Thread(target=event_listener)
]

for t in threads:
    t.start()

threads[-1].join()
