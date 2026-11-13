"""Desktop simulation of the real board entry point; never connects to an ESP32.

Run from the repository root: python3 read_temp/demo_main.py
All state and readings files live in a temporary flat board directory.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARD_FILES = (
    ("read_temp/main.py", "main.py"),
    ("read_temp/config.py", "config.py"),
    ("read_temp/scheduler.py", "scheduler.py"),
    ("store_readings/storage.py", "storage.py"),
    ("exposure/exposure_limits.py", "exposure_limits.py"),
    ("exposure/freeze_exposure.py", "freeze_exposure.py"),
    ("exposure/freeze_state.py", "freeze_state.py"),
    ("exposure/heat_exposure/heat_exposure.py", "heat_exposure.py"),
    ("exposure/heat_exposure/heat_state.py", "heat_state.py"),
    ("vaccine_profile/comparison.py", "comparison.py"),
    ("vaccine_profile/profile_loader.py", "profile_loader.py"),
    ("vaccine_profile/profile_check.py", "profile_check.py"),
)

# Executed by isolated desktop Python in the staged board directory. Only
# hardware, time, and socket access are replaced; application modules are real.
WORKER = r'''
import importlib
import io
import json
import os
import socket
import sys
import types
from contextlib import redirect_stdout

sys.path.insert(0, os.getcwd())
scenario = json.load(sys.stdin)
values = list(scenario["values"])
count = len(values)

class Sensor:
    def __init__(self, pin):
        self.current = None
    def measure(self):
        self.current = values.pop(0)
        if self.current == "error":
            raise OSError("sensor_timeout")
    def temperature(self):
        return self.current

def no_network(*args, **kwargs):
    raise RuntimeError("network access attempted during offline simulation")

socket.socket = socket.create_connection = socket.getaddrinfo = no_network
sys.modules["machine"] = types.SimpleNamespace(Pin=lambda pin: pin)
sys.modules["dht"] = types.SimpleNamespace(DHT22=Sensor)

def write_json(path, value):
    with open(path, "w") as stream:
        json.dump(value, stream)

write_json("config.json", {"interval_s": 60})
write_json("exposure_limits.json", {"upper_limit_c": 8.0, "lower_limit_c": 2.0})
write_json("profile.json", scenario["profile"])
for side in ("heat", "freeze"):
    total = scenario["initial_" + side + "_s"]
    if total is not None:
        write_json(side + "_state.json", {
            side + "_s": total,
            "last_good": {"timestamp_s": -60, "temp_c": 4.0, "ok": True,
                          "shipment_id": "SHP-1001"},
        })

import main
from storage import load_readings

now = [0]
snapshots = []
serial = io.StringIO()

def snapshot(record):
    return {"timestamp_s": record["timestamp_s"], "temp_c": record["temp_c"],
            "ok": record["ok"], "heat_s": main.heat["heat_s"],
            "freeze_s": main.freeze["freeze_s"], "comparison": main.comparison_result}

def collect(record):
    with redirect_stdout(serial):
        main.emit(record)
    snapshots.append(snapshot(record))

def sleep(seconds):
    now[0] += seconds

main.Scheduler(main.read, collect, main.DEVICE_ID, main.SHIPMENT_ID,
               clock=lambda: now[0], sleep=sleep).run(max_reads=count)
restored = after_restart = None
if scenario["restart"]:
    main = importlib.reload(main)
    restored = {"heat_s": main.heat["heat_s"], "freeze_s": main.freeze["freeze_s"]}
    record = {"device_id": main.DEVICE_ID, "shipment_id": main.SHIPMENT_ID,
              "seq": 1, "timestamp_s": now[0], "temp_c": 4.0, "ok": True, "error": None}
    with redirect_stdout(serial):
        main.emit(record)
    after_restart = snapshot(record)

stored, skipped = load_readings()
with open("heat_state.json") as stream:
    saved_heat_s = json.load(stream)["heat_s"]
with open("freeze_state.json") as stream:
    saved_freeze_s = json.load(stream)["freeze_s"]
print(json.dumps({"snapshots": snapshots, "restored": restored,
                  "after_restart": after_restart, "stored": stored, "skipped": skipped,
                  "serial": [json.loads(line) for line in serial.getvalue().splitlines()],
                  "saved_heat_s": saved_heat_s, "saved_freeze_s": saved_freeze_s}))
'''


def run_simulation(values, profile, restart=False, initial_heat_s=None, initial_freeze_s=None):
    """Run real board files with synthetic readings in an isolated desktop process."""
    scenario = {"values": values, "profile": profile, "restart": restart,
                "initial_heat_s": initial_heat_s, "initial_freeze_s": initial_freeze_s}
    with tempfile.TemporaryDirectory() as directory:
        for source, target in BOARD_FILES:
            shutil.copyfile(os.path.join(ROOT, source), os.path.join(directory, target))
        result = subprocess.run(
            [sys.executable, "-I", "-c", WORKER], cwd=directory,
            input=json.dumps(scenario), text=True, capture_output=True, timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError("Desktop board simulation failed:\n" + result.stderr)
        return json.loads(result.stdout)


def main():
    print("DESKTOP SIMULATION: real board code, simulated sensor/time, network blocked")
    print("Synthetic profile limits: heat 119 s, freeze 120 s")
    result = run_simulation([9.0, 9.0, 1.0, 1.0, 4.0, "error", 4.0],
                            {"heat_limit_s": 119, "freeze_limit_s": 120}, restart=True)
    for item in result["snapshots"]:
        print("t=%3d s temp=%s heat=%d s freeze=%d s -> %s" % (
            item["timestamp_s"], item["temp_c"], item["heat_s"], item["freeze_s"],
            json.dumps(item["comparison"])))
    print("Restored after simulated program restart: %s" % json.dumps(result["restored"]))
    print("After another warm reading: %s" % json.dumps(result["after_restart"]["comparison"]))
    print("Stored %d readings, including the failed reading; skipped=%d" % (
        len(result["stored"]), result["skipped"]))
    broken = run_simulation([4.0], {"heat_limit_s": 119})
    print("Broken profile -> %s" % json.dumps(broken["snapshots"][0]["comparison"]))


if __name__ == "__main__":
    main()
