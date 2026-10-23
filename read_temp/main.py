# Read temperature with the DHT22 on the configured interval (story 003-1).
# Runs on ESP32 MicroPython in Wokwi. Needs config.py and scheduler.py on the board.
#
# The driver is read(): it returns °C or raises when the sensor fails. The
# Scheduler adds device_id, shipment_id, seq and timestamp_s, waits interval_s
# from config.json, and emits a failed read as a record too (ok=false).
import json

from machine import Pin
from dht import DHT22

from scheduler import Scheduler

# Sprint 1 uses fixed test values (see the temperature data format agreement, item 9).
DEVICE_ID = "BOX-001"
SHIPMENT_ID = "SHP-1001"

dht = DHT22(Pin(4))


def read():
    """Return the temperature in °C. Raises OSError when the sensor fails."""
    dht.measure()
    return dht.temperature()


def emit(record):
    """Log each record to the serial monitor as one JSON line."""
    print(json.dumps(record))


def main():
    Scheduler(read, emit, DEVICE_ID, SHIPMENT_ID).run()


if __name__ == "__main__":
    main()
