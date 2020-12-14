from datetime import datetime, timedelta
from typing import Dict
from uuid import uuid4

from tokens.services.scheduler import Scheduler, ScheduledEvent
from tokens.services.token import Token
from tokens.services.token_storage import TokenStorage

DEFAULT_TOKEN_TTL = timedelta(seconds=30)
DEFAULT_KEEPALIVE_TTL = timedelta(seconds=60)


class TokenManager:
    scheduled_delete_events: Dict[str, ScheduledEvent] = {}
    scheduled_unassign_events: Dict[str, ScheduledEvent] = {}

    def __init__(self, token_storage: TokenStorage, scheduler: Scheduler):
        self.token_storage = token_storage
        self.scheduler = scheduler

    def generate(self):
        token_id = str(uuid4())
        expiry = datetime.utcnow() + DEFAULT_KEEPALIVE_TTL
        token = Token(token_id, expiry=expiry, allocated=False)

        self.token_storage.add(token)

        delete_event = self.scheduler.schedule(expiry, lambda: self.delete(token))
        self.scheduled_delete_events[token_id] = delete_event

        return token

    def assign(self):
        token = self.token_storage.assign()

        if not token:
            return None

        unassign_time = datetime.utcnow() + DEFAULT_TOKEN_TTL
        unassign_event = self.scheduler.schedule(unassign_time, lambda: self.unassign(token))
        self.scheduled_unassign_events[token.id] = unassign_event

        return token

    def unassign(self, token: Token):
        token_id = token.id

        if token_id in self.scheduled_unassign_events:
            scheduled_unassign_event = self.scheduled_unassign_events[token_id]
            self.scheduler.delete(scheduled_unassign_event)
            del self.scheduled_unassign_events[token_id]

        self.token_storage.unassign(token_id)

    def delete(self, token: Token):
        self.unassign(token)

        token_id = token.id
        if token_id in self.scheduled_delete_events:
            scheduled_delete_event = self.scheduled_delete_events[token_id]
            self.scheduler.delete(scheduled_delete_event)
            del self.scheduled_delete_events[token_id]

        self.token_storage.delete(token_id)

    def keep_alive(self, token: Token):
        expiry = datetime.utcnow() + DEFAULT_KEEPALIVE_TTL
        token.expiry = expiry

        token_id = token.id

        if token_id in self.scheduled_unassign_events:
            scheduled_unassign_event = self.scheduled_unassign_events[token_id]
            self.scheduler.delete(scheduled_unassign_event)
            self.scheduled_unassign_events[token_id] = self.scheduler.schedule(expiry,
                                                                               lambda: self.unassign(token))

        if token_id in self.scheduled_delete_events:
            scheduled_delete_event = self.scheduled_delete_events[token_id]
            self.scheduler.delete(scheduled_delete_event)
            self.scheduled_delete_events[token_id] = self.scheduler.schedule(expiry, lambda: self.delete(token))
