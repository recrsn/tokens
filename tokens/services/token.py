from dataclasses import dataclass
from datetime import datetime


@dataclass
class Token:
    id: str
    expiry: datetime
    allocated: bool
