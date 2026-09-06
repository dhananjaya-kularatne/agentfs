"""
Small in-process sliding-window rate limiter.

The agent task endpoints are unauthenticated and each call fans out to as
many as ten LLM requests, so an open endpoint is a cheap way to burn the
deployment's Groq quota. This keeps a per-key timestamp window in memory and
rejects callers that exceed the configured budget.

In-memory means the limit is per process and resets on restart; for a
single-instance demo that is enough. A multi-instance deployment would move
this to a shared store (e.g. Redis).
"""

import threading
import time
from collections import defaultdict, deque

from app.config import settings


class RateLimiter:
    def __init__(self, max_events: int, window_seconds: float):
        self.max_events = max_events
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        """Record a hit for key and return whether it is within budget."""
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] < cutoff:
                hits.popleft()
            if len(hits) >= self.max_events:
                return False
            hits.append(now)
            return True

    def retry_after(self, key: str) -> int:
        """Seconds until the oldest recorded hit for key leaves the window."""
        with self._lock:
            hits = self._hits.get(key)
            if not hits:
                return 0
            return max(1, int(self.window_seconds - (time.monotonic() - hits[0])) + 1)


task_rate_limiter = RateLimiter(
    max_events=settings.rate_limit_max_tasks,
    window_seconds=settings.rate_limit_window_seconds,
)
