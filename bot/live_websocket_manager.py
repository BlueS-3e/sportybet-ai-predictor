"""
Live WebSocket Manager for Real-Time Sports Data
Handles live odds, scores, and match events streaming
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Callable
from collections import defaultdict

logger = logging.getLogger(__name__)


class LiveWebSocketManager:
    """Manages WebSocket connections for live sports data"""
    
    def __init__(self, bot_instance=None):
        self.bot = bot_instance
        self.connections = {}
        self.subscriptions = defaultdict(set)  # {user_id: set of match_ids}
        self.active_matches = {}
        self.callbacks = []
        self.is_running = False
        
    async def connect_to_odds_provider(self, provider: str = 'odds_api'):
        """Connect to live odds WebSocket provider"""
        providers = {
            'odds_api': 'wss://api.the-odds-api.com/v4/stream',
            'betfair': 'wss://stream-api.betfair.com/api/v1/stream',
            'custom': 'wss://your-backend.com/live/odds'
        }
        
        url = providers.get(provider, providers['custom'])
        
        while self.is_running:
            try:
                async with websockets.connect(url) as websocket:
                    logger.info(f"✅ Connected to {provider} WebSocket")
                    
                    # Subscribe to markets
                    subscribe_msg = {
                        "op": "subscribe",
                        "channel": "odds",
                        "markets": ["h2h", "spreads", "totals"],
                        "sports": ["soccer"],
                        "regions": ["eu", "uk", "us"]
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                    
                    # Listen for updates
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            await self.process_odds_update(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error: {e}")
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"WebSocket connection closed. Reconnecting in 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(10)
    
    async def connect_to_live_scores(self):
        """Connect to live scores WebSocket"""
        url = "wss://livescore-api.com/v1/stream"
        
        while self.is_running:
            try:
                async with websockets.connect(url) as websocket:
                    logger.info("✅ Connected to live scores WebSocket")
                    
                    # Subscribe to live matches
                    subscribe_msg = {
                        "action": "subscribe",
                        "events": ["goal", "red_card", "yellow_card", "match_start", "match_end"]
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                    
                    async for message in websocket:
                        data = json.loads(message)
                        await self.process_live_event(data)
                        
            except Exception as e:
                logger.error(f"Live scores WebSocket error: {e}")
                await asyncio.sleep(5)
    
    async def process_odds_update(self, data: Dict):
        """Process incoming odds data"""
        try:
            match_id = data.get('id')
            bookmakers = data.get('bookmakers', [])
            
            if not match_id:
                return
            
            # Update stored odds
            self.active_matches[match_id] = {
                'odds': bookmakers,
                'timestamp': datetime.now().isoformat(),
                'home_team': data.get('home_team'),
                'away_team': data.get('away_team')
            }
            
            # Check for significant odds changes
            await self.check_odds_alerts(match_id, bookmakers)
            
            # Broadcast to subscribers
            await self.notify_subscribers(match_id, 'odds_update', data)
            
        except Exception as e:
            logger.error(f"Error processing odds update: {e}")
    
    async def process_live_event(self, data: Dict):
        """Process live match events (goals, cards, etc.)"""
        try:
            event_type = data.get('type')
            match_id = data.get('match_id')
            
            if event_type == 'goal':
                await self.handle_goal_event(match_id, data)
            elif event_type == 'red_card':
                await self.handle_red_card_event(match_id, data)
            elif event_type == 'match_start':
                await self.handle_match_start(match_id, data)
            elif event_type == 'match_end':
                await self.handle_match_end(match_id, data)
            
            # Broadcast to subscribers
            await self.notify_subscribers(match_id, event_type, data)
            
        except Exception as e:
            logger.error(f"Error processing live event: {e}")
    
    async def handle_goal_event(self, match_id: str, data: Dict):
        """Handle goal scored event"""
        message = (
            f"⚽ **GOAL!** ⚽\n"
            f"{data.get('home_team')} {data.get('score_home')} - "
            f"{data.get('score_away')} {data.get('away_team')}\n"
            f"⏱️ {data.get('minute')}' - {data.get('scorer', 'Unknown')}\n"
            f"📊 Live odds updated!"
        )
        
        await self.broadcast_to_match_subscribers(match_id, message)
    
    async def handle_red_card_event(self, match_id: str, data: Dict):
        """Handle red card event"""
        message = (
            f"🟥 **RED CARD!** 🟥\n"
            f"{data.get('home_team')} vs {data.get('away_team')}\n"
            f"⏱️ {data.get('minute')}' - {data.get('player', 'Unknown')}\n"
            f"⚠️ {data.get('team')} down to 10 players!"
        )
        
        await self.broadcast_to_match_subscribers(match_id, message)
    
    async def handle_match_start(self, match_id: str, data: Dict):
        """Handle match start event"""
        message = (
            f"🏁 **KICK OFF!** 🏁\n"
            f"{data.get('home_team')} vs {data.get('away_team')}\n"
            f"🏆 {data.get('league', 'Unknown League')}\n"
            f"📊 Live predictions available!"
        )
        
        await self.broadcast_to_match_subscribers(match_id, message)
    
    async def handle_match_end(self, match_id: str, data: Dict):
        """Handle match end event"""
        message = (
            f"🏁 **FULL TIME!** 🏁\n"
            f"{data.get('home_team')} {data.get('score_home')} - "
            f"{data.get('score_away')} {data.get('away_team')}\n"
            f"📊 Final result confirmed!"
        )
        
        await self.broadcast_to_match_subscribers(match_id, message)
        
        # Clean up match from active matches
        if match_id in self.active_matches:
            del self.active_matches[match_id]
    
    async def check_odds_alerts(self, match_id: str, bookmakers: List[Dict]):
        """Check for user alert triggers based on odds changes"""
        # Get best odds
        best_home = max((b.get('home', 0) for b in bookmakers), default=0)
        best_away = max((b.get('away', 0) for b in bookmakers), default=0)
        
        # Check user alerts from database
        # This would integrate with your monetization_db
        alerts = await self.get_user_alerts(match_id)
        
        for alert in alerts:
            if self.check_alert_condition(alert, best_home, best_away):
                await self.trigger_alert(alert)
    
    async def get_user_alerts(self, match_id: str) -> List[Dict]:
        """Get active user alerts for a match"""
        # TODO: Integrate with database
        return []
    
    def check_alert_condition(self, alert: Dict, home_odds: float, away_odds: float) -> bool:
        """Check if alert condition is met"""
        condition = alert.get('condition', {})
        alert_type = condition.get('type')
        
        if alert_type == 'odds_threshold':
            target_odds = condition.get('target_odds', 0)
            team = condition.get('team', 'home')
            current_odds = home_odds if team == 'home' else away_odds
            return current_odds >= target_odds
        
        return False
    
    async def trigger_alert(self, alert: Dict):
        """Send alert notification to user"""
        user_id = alert.get('user_id')
        message = alert.get('message', 'Your alert has been triggered!')
        
        if self.bot:
            try:
                await self.bot.application.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to send alert to user {user_id}: {e}")
    
    async def notify_subscribers(self, match_id: str, event_type: str, data: Dict):
        """Notify all subscribers of a match about an event"""
        subscribers = self.subscriptions.get(match_id, set())
        
        for user_id in subscribers:
            # Execute registered callbacks
            for callback in self.callbacks:
                try:
                    await callback(user_id, event_type, data)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
    
    async def broadcast_to_match_subscribers(self, match_id: str, message: str):
        """Send message to all users subscribed to a match"""
        subscribers = self.subscriptions.get(match_id, set())
        
        if self.bot:
            for user_id in subscribers:
                try:
                    await self.bot.application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Failed to notify user {user_id}: {e}")
    
    def subscribe_user(self, user_id: int, match_id: str):
        """Subscribe a user to match updates"""
        self.subscriptions[match_id].add(user_id)
        logger.info(f"User {user_id} subscribed to match {match_id}")
    
    def unsubscribe_user(self, user_id: int, match_id: str):
        """Unsubscribe a user from match updates"""
        if match_id in self.subscriptions:
            self.subscriptions[match_id].discard(user_id)
            logger.info(f"User {user_id} unsubscribed from match {match_id}")
    
    def register_callback(self, callback: Callable):
        """Register a callback for match events"""
        self.callbacks.append(callback)
    
    async def start(self):
        """Start the WebSocket manager"""
        self.is_running = True
        logger.info("🚀 Starting Live WebSocket Manager...")
        
        # Start multiple WebSocket connections
        tasks = [
            asyncio.create_task(self.connect_to_odds_provider()),
            asyncio.create_task(self.connect_to_live_scores()),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop(self):
        """Stop the WebSocket manager"""
        self.is_running = False
        logger.info("🛑 Stopping Live WebSocket Manager...")


# Singleton instance
_websocket_manager = None


def get_websocket_manager(bot_instance=None):
    """Get or create WebSocket manager instance"""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = LiveWebSocketManager(bot_instance)
    return _websocket_manager
