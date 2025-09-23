from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ServiceConfig:
    url: str
    prefix: str
    health_path: str = "/health"

@dataclass
class CircuitBreakerState:
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

@dataclass
class RateLimitState:
    requests: List[float] = field(default_factory=list)
    blocked_until: Optional[datetime] = None