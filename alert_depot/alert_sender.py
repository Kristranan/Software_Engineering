# Send alerts to the depot (story 007-1, AC5).
# Runs on ESP32 MicroPython and on desktop CPython (for tests).
#
# network and depot are passed in (duck typing), so tests need no real
# network: network.is_online() -> bool, depot.receive(event) -> None.


class AlertSender:
    def __init__(self, network, depot):
        self._network = network
        self._depot = depot
        self._queue = []

    def send(self, event):
        """Deliver the event now when there is signal; otherwise queue it."""
        if self._network.is_online():
            self._depot.receive(event)
        else:
            self._queue.append(event)

    def pending_count(self):
        """How many alerts are still waiting to be delivered."""
        return len(self._queue)
