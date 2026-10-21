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
        """Queue the event, then deliver everything waiting if there is signal.

        Going through the queue keeps the order: alerts queued while offline
        reach the depot before a new one.
        """
        self._queue.append(event)
        self.flush()

    def flush(self):
        """When there is signal, deliver every queued alert in order, each once."""
        if not self._network.is_online():
            return
        while self._queue:
            # Remove an alert only after the depot has it, so none is lost.
            self._depot.receive(self._queue[0])
            self._queue.pop(0)

    def pending_count(self):
        """How many alerts are still waiting to be delivered."""
        return len(self._queue)
