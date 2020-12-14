from dataclasses import dataclass
from datetime import datetime
from threading import Thread
from typing import Dict, Callable, List
from uuid import uuid4

from time import sleep


@dataclass
class ScheduledEvent:
    id: str
    time: datetime
    action: Callable


class Scheduler:
    scheduled_events: Dict[str, ScheduledEvent] = {}
    events_by_unix_epoch: Dict[int, List[str]] = {}
    running = False

    def schedule(self, time: datetime, action: Callable):
        event_id = str(uuid4())
        event = ScheduledEvent(id=event_id, time=time, action=action)

        self.scheduled_events[event_id] = event

        time_in_unix_epoch = int(time.timestamp())

        if time_in_unix_epoch not in self.events_by_unix_epoch:
            self.events_by_unix_epoch[time_in_unix_epoch] = []

        self.events_by_unix_epoch[time_in_unix_epoch].append(event_id)

        return event

    def delete(self, event: ScheduledEvent):
        if event.id in self.scheduled_events:
            del self.scheduled_events[event.id]

        time_in_unix_epoch = int(event.time.timestamp())

        if time_in_unix_epoch in self.events_by_unix_epoch:
            self.events_by_unix_epoch[time_in_unix_epoch].remove(event.id)

    def start(self):
        running = True

        def scheduler_loop():
            while running:
                current_unix_epoch = int(datetime.utcnow().timestamp())

                if current_unix_epoch in self.events_by_unix_epoch:
                    events = self.events_by_unix_epoch.pop(current_unix_epoch, [])

                    for event_id in events:
                        event = self.scheduled_events.pop(event_id)
                        event.action()

                sleep(1)

        t = Thread(target=scheduler_loop)
        t.setDaemon(True)
        t.start()

    def stop(self):
        self.running = False
