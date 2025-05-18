from collections import OrderedDict
from datetime import datetime, timedelta
import threading
from uuid import uuid4
from typing import Dict, List, Optional, Tuple

class LRUCache:
    def __init__(self, expiry_minutes: int = 15):
        self._cache: OrderedDict = OrderedDict()
        self._lock = threading.Lock()
        self._expiry_delta = timedelta(minutes=expiry_minutes)

    def _is_expired(self, timestamp: datetime) -> bool:
        return datetime.now() - timestamp > self._expiry_delta

    def get(self, key: str) -> Optional[Tuple]:
        with self._lock:
            if key not in self._cache:
                return None
            
            value, session_id, timestamp = self._cache[key]
            
            if self._is_expired(timestamp):
                del self._cache[key]
                return None
                
            # Move to end to mark as recently used
            self._cache.move_to_end(key)
            return value, session_id

    def set(self, key: str, session_data: List[Dict] = []) -> str:
        with self._lock:
            session_id = str(uuid4())
            value = {
                "session": session_data,
            }
            self._cache[key] = (value, session_id, datetime.now())
            self._cache.move_to_end(key)
            return session_id

    def add_interaction(self, key: str, request: str, response: str) -> None:
        with self._lock:
            if key in self._cache:
                value, session_id, _ = self._cache[key]
                value["session"].append({
                    "request": request,
                    "response": response
                })
                self._cache[key] = (value, session_id, datetime.now())
                self._cache.move_to_end(key)

    def clear_expired(self) -> None:
        """Remove all expired entries from cache"""
        with self._lock:
            expired_keys = [
                key for key, (_, _, timestamp) in self._cache.items()
                if self._is_expired(timestamp)
            ]
            for key in expired_keys:
                del self._cache[key]

    def clear(self) -> None:
        """Remove all entries from cache"""
        with self._lock:
            self._cache.clear()
