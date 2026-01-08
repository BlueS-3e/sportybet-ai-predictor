"""
Business Analytics Module
Tracks user engagement, revenue, and bot performance metrics
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class BusinessAnalytics:
    """Tracks business metrics"""
    
    def __init__(self):
        """Initialize analytics"""
        self.events = []
        self.user_events = defaultdict(list)
        self.revenue_tracker = defaultdict(float)
        logger.info("📊 Business analytics initialized")
    
    def track_event(self, user_id: int, event_type: str, metadata: Dict = None):
        """Track user event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'event_type': event_type,
            'metadata': metadata or {}
        }
        
        self.events.append(event)
        self.user_events[user_id].append(event)
        
        logger.debug(f"📝 Event tracked: {event_type} (user: {user_id})")
    
    def track_prediction(self, user_id: int, match: str, prediction: str, 
                        confidence: float, stake: float = 0.0):
        """Track prediction"""
        self.track_event(user_id, 'prediction_made', {
            'match': match,
            'prediction': prediction,
            'confidence': confidence,
            'stake': stake
        })
    
    def track_conversion(self, user_id: int, tier: str, amount: float):
        """Track subscription conversion"""
        self.track_event(user_id, 'subscription_upgrade', {
            'tier': tier,
            'amount': amount
        })
        self.revenue_tracker[tier] += amount
        logger.info(f"💰 Conversion: user {user_id} → {tier} (+${amount:.2f})")
    
    def get_user_metrics(self, user_id: int) -> Dict:
        """Get user metrics"""
        events = self.user_events.get(user_id, [])
        
        predictions = [e for e in events if e['event_type'] == 'prediction_made']
        conversions = [e for e in events if e['event_type'] == 'subscription_upgrade']
        
        total_stake = sum(e['metadata'].get('stake', 0) for e in predictions)
        
        return {
            'user_id': user_id,
            'total_events': len(events),
            'total_predictions': len(predictions),
            'total_conversions': len(conversions),
            'lifetime_value': sum(e['metadata'].get('amount', 0) for e in conversions),
            'total_stake': total_stake,
            'first_seen': events[0]['timestamp'] if events else None,
            'last_seen': events[-1]['timestamp'] if events else None
        }
    
    def get_dashboard_metrics(self) -> Dict:
        """Get overall business dashboard metrics"""
        total_users = len(self.user_events)
        total_predictions = sum(
            1 for e in self.events 
            if e['event_type'] == 'prediction_made'
        )
        total_conversions = sum(
            1 for e in self.events 
            if e['event_type'] == 'subscription_upgrade'
        )
        total_revenue = sum(self.revenue_tracker.values())
        
        # Calculate metrics
        conversion_rate = (total_conversions / total_users * 100) if total_users > 0 else 0
        avg_predictions_per_user = (total_predictions / total_users) if total_users > 0 else 0
        avg_revenue_per_user = (total_revenue / total_users) if total_users > 0 else 0
        
        return {
            'total_users': total_users,
            'total_predictions': total_predictions,
            'total_conversions': total_conversions,
            'conversion_rate': conversion_rate,
            'total_revenue': total_revenue,
            'avg_predictions_per_user': avg_predictions_per_user,
            'avg_revenue_per_user': avg_revenue_per_user,
            'revenue_by_tier': dict(self.revenue_tracker),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_retention_metrics(self, days: int = 7) -> Dict:
        """Get retention metrics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        active_users = set()
        for user_id, events in self.user_events.items():
            for event in events:
                event_time = datetime.fromisoformat(event['timestamp'])
                if event_time > cutoff_date:
                    active_users.add(user_id)
                    break
        
        return {
            'period_days': days,
            'active_users': len(active_users),
            'total_users': len(self.user_events),
            'retention_rate': (len(active_users) / len(self.user_events) * 100) 
                            if self.user_events else 0
        }
    
    def get_prediction_accuracy(self, user_id: Optional[int] = None) -> Dict:
        """Get prediction accuracy statistics"""
        events = self.user_events.get(user_id, []) if user_id else self.events
        
        predictions = [e for e in events if e['event_type'] == 'prediction_made']
        correct = sum(1 for e in predictions if e['metadata'].get('correct'))
        total = len(predictions)
        
        return {
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy': (correct / total * 100) if total > 0 else 0
        }
    
    def get_revenue_forecast(self, days_ahead: int = 30) -> Dict:
        """Get revenue forecast"""
        # Simple linear regression based on recent trend
        recent_revenue = sum(
            1 for e in self.events 
            if e['event_type'] == 'subscription_upgrade' and
            datetime.fromisoformat(e['timestamp']) > 
            (datetime.now() - timedelta(days=7))
        )
        
        daily_rate = recent_revenue / 7
        projected_revenue = daily_rate * days_ahead
        
        return {
            'forecast_period_days': days_ahead,
            'daily_conversion_rate': daily_rate,
            'projected_conversions': int(projected_revenue),
            'projected_revenue': projected_revenue * 5.0,  # Avg tier price
            'confidence': 'Low'  # Since it's simple extrapolation
        }


# Global instance
_analytics = None


def get_analytics() -> BusinessAnalytics:
    """Get or create analytics instance"""
    global _analytics
    if _analytics is None:
        _analytics = BusinessAnalytics()
    return _analytics
