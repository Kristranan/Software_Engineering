# Accumulate heat exposure (story 004-1). Owner: Reef.
# Runs on ESP32 MicroPython and on desktop CPython (for tests): plain dicts,
# no dataclasses, no typing module.
#
# Rule R1 (agreed with Sia for freeze too):
# the time between two good readings is counted by the earlier one. If the
# earlier reading was above upper_limit_c, the whole time between them is
# heat time.
#
# Everything here is pure: no file, no clock, no network. The heat code
# never reads or writes freeze (AC1).


def is_good_reading(record):
    """True when the read worked: ok is True and temp_c is a number."""
    if record is None or record.get("ok") is not True:
        return False
    temp = record.get("temp_c")
    return not isinstance(temp, bool) and isinstance(temp, (int, float))


def heat_increment_s(last_good, record, upper_limit_c):
    """Seconds of heat to add when `record` arrives. Always an int >= 0 (AC2).

    last_good: the last good reading before `record`, or None for the first one.
    "Above" means strictly greater than upper_limit_c (8.0 is not heat, 8.1 is).

    Adds 0 when:
      - there is no earlier good reading yet
      - `record` is a failed read (the gap is counted at the next good reading)
      - time stands still or goes backwards (for example after a power cut,
        when the clock restarts)
      - the earlier reading was not above the limit
    """
    if not is_good_reading(last_good) or not is_good_reading(record):
        return 0
    gap_s = int(record["timestamp_s"]) - int(last_good["timestamp_s"])
    if gap_s <= 0:
        return 0
    if last_good["temp_c"] > upper_limit_c:
        return gap_s
    return 0