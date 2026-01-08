"""
Caching utilities for predictions with TTL support
"""
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PredictionCache:
    """Simple in-memory prediction cache with TTL"""
    
    def __init__(self, ttl_seconds: int = 3600):
        """Initialize cache with TTL (default 1 hour)"""
        self.cache: Dict[str, Dict] = {}
        self.timestamps: Dict[str, datetime] = {}
        self.ttl = ttl_seconds
    
    def _make_key(self, home_team: str, away_team: str) -> str:
        """Create a cache key from team names"""
        return f"{home_team.lower()}_{away_team.lower()}".replace(" ", "_")
    
    def get(self, home_team: str, away_team: str) -> Optional[Dict]:
        """Get cached prediction if available and not expired"""
        key = self._make_key(home_team, away_team)
        
        if key not in self.cache:
            return None
        
        # Check if expired
        if key in self.timestamps:
            age = (datetime.now() - self.timestamps[key]).total_seconds()
            if age > self.ttl:
                del self.cache[key]
                del self.timestamps[key]
                return None
        
        return self.cache[key]
    
    def set(self, prediction: Dict, home_team: str, away_team: str) -> None:
        """Cache a prediction"""
        key = self._make_key(home_team, away_team)
        self.cache[key] = prediction
        self.timestamps[key] = datetime.now()
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        self.timestamps.clear()
    
    def cleanup_expired(self) -> None:
        """Remove expired entries"""
        now = datetime.now()
        expired_keys = [
            key for key, ts in self.timestamps.items()
            if (now - ts).total_seconds() > self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]
            del self.timestamps[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
