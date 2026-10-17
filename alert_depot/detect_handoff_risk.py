# Red alert at handoff (story 007-1, AC3).
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# When the box shows RED at the clinic handoff, build a RED_AT_HANDOFF risk
# event so the depot is alerted immediately. A GREEN handoff gives no alert.

import contracts


def detect_handoff_risk(handoff):
    """Detects risk at handoff based on the box status at the clinic.

    Args:
        handoff (dict): A dictionary containing the handoff information, including the 'status' key.

    Returns:
        dict: a RED_AT_HANDOFF risk event if the handoff status is RED, otherwise None.
    """
    if handoff.get('status') == contracts.RED:

        return {'type': contracts.RED_AT_HANDOFF,
                'device_id': handoff.get('device_id'),
                'shipment_id': handoff.get('shipment_id'),
                'timestamp_s': handoff.get('timestamp_s')}
    else:
        return None
