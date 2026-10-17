# Scheduler: read the temperature every interval_s (story 003-1).
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# Everything from the outside world is passed in, so the same code runs with
# the mock sensor now and the real driver later, and tests need no hardware,
# real clock or network:
#   read()       -> temperature in °C, or raises when the sensor fails
#   emit(record) -> receives each reading record
#   clock()      -> seconds (time.time on the box)
#   sleep(s)     -> waits s seconds
#
# No network is used. On boot the interval comes from config.json (or the
# defaults), so after a power cut the box starts reading again by itself.
# seq restarts at 1 on every boot: keeping it across power cuts needs on-box
# storage (story 003-2), which is not in Sprint 1.
import time

import config

# Field names follow alert_depot/contracts.py.
RECORD_KEYS = ("device_id", "shipment_id", "seq", "timestamp_s", "temp_c", "ok", "error")


class Scheduler:
    def __init__(self, read, emit, device_id, shipment_id,
                 clock=time.time, sleep=time.sleep, config_path=config.CONFIG_PATH):
        self.interval_s = config.load(config_path)["interval_s"]
        self.device_id = device_id
        self.shipment_id = shipment_id
        self.seq = 0
        self._read = read
        self._emit = emit
        self._clock = clock
        self._sleep = sleep

    def read_once(self):
        """Read once and emit a record. A failed read is emitted too, never skipped."""
        self.seq += 1
        record = {
            "device_id": self.device_id,
            "shipment_id": self.shipment_id,
            "seq": self.seq,
            "timestamp_s": int(self._clock()),
            "temp_c": None,
            "ok": False,
            "error": None,
        }
        try:
            record["temp_c"] = self._read()
            record["ok"] = True
        except Exception as e:
            record["error"] = str(e) or type(e).__name__
        self._emit(record)
        return record

    def run(self, max_reads=None):
        """Read, then wait interval_s, forever (or max_reads times, for tests)."""
        count = 0
        while max_reads is None or count < max_reads:
            self.read_once()
            count += 1
            self._sleep(self.interval_s)
