"""
Live Update Service - Polls APIs and manages real-time data
Scheduler for live matches, odds, and alerts
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class LiveUpdateService:
    """Service for managing live updates via polling"""
    
    def __init__(self, bot_instance, database):
        self.bot = bot_instance
        self.db = database
        self.scheduler = AsyncIOScheduler()
        self.active_matches = {}
        self.odds_history = {}
        
    def start(self):
        """Start the live update service"""
        logger.info("🚀 Starting Live Update Service...")
        
        # Update live matches every 30 seconds
        self.scheduler.add_job(
            self.update_live_matches,
            IntervalTrigger(seconds=30),
            id='live_matches',
            name='Update Live Matches',
            replace_existing=True
        )
        
        # Update odds every 60 seconds
        self.scheduler.add_job(
            self.update_odds,
            IntervalTrigger(seconds=60),
            id='odds_update',
            name='Update Odds',
            replace_existing=True
        )
        
        # Check for alerts every 10 seconds
        self.scheduler.add_job(
            self.check_alerts,
            IntervalTrigger(seconds=10),
            id='alert_check',
            name='Check User Alerts',
            replace_existing=True
        )
        
        # Update statistics every 5 minutes
        self.scheduler.add_job(
            self.update_statistics,
            IntervalTrigger(minutes=5),
            id='stats_update',
            name='Update Match Statistics',
            replace_existing=True
        )
        
        # Scan for arbitrage opportunities every 2 minutes
        self.scheduler.add_job(
            self.scan_arbitrage,
            IntervalTrigger(minutes=2),
            id='arbitrage_scan',
            name='Arbitrage Scanner',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("✅ Live Update Service started successfully")
    
    async def update_live_matches(self):
        """Fetch and update live matches from API"""
        try:
            # Fetch live matches from your API/data source
            matches = await self.fetch_live_matches()
            
            for match in matches:
                match_id = match.get('id')
                
                # Check if match already being tracked
                if match_id in self.active_matches:
                    old_match = self.active_matches[match_id]
                    
                    # Detect score changes
                    if (match.get('score_home') != old_match.get('score_home') or
                        match.get('score_away') != old_match.get('score_away')):
                        await self.notify_score_change(match, old_match)
                    
                    # Detect status changes
                    if match.get('status') != old_match.get('status'):
                        await self.notify_status_change(match, old_match)
                    
                    # Detect minute changes (for in-play predictions)
                    if match.get('minute') != old_match.get('minute'):
                        await self.update_inplay_predictions(match)
                else:
                    # New live match detected
                    await self.notify_match_started(match)
                
                # Store updated match data
                self.active_matches[match_id] = match
            
            # Remove finished matches
            finished_matches = [
                mid for mid, m in self.active_matches.items()
                if m.get('status') in ['finished', 'postponed', 'cancelled']
            ]
            for match_id in finished_matches:
                await self.handle_match_finished(match_id)
                del self.active_matches[match_id]
                
        except Exception as e:
            logger.error(f"Error updating live matches: {e}")
    
    async def fetch_live_matches(self) -> List[Dict]:
        """Fetch live matches from external API"""
        # TODO: Integrate with real API (football-data.org, api-football, etc.)
        # Placeholder implementation
        return [
            {
                'id': 'match_001',
                'home': 'Manchester City',
                'away': 'Arsenal',
                'score_home': 2,
                'score_away': 1,
                'minute': 78,
                'status': 'live',
                'league': 'Premier League'
            }
        ]
    
    async def update_odds(self):
        """Update odds for all tracked matches"""
        try:
            for match_id in self.active_matches.keys():
                odds = await self.fetch_odds(match_id)
                
                if match_id in self.odds_history:
                    old_odds = self.odds_history[match_id]
                    
                    # Detect significant odds movement
                    if self.detect_odds_movement(old_odds, odds):
                        await self.notify_odds_change(match_id, old_odds, odds)
                
                self.odds_history[match_id] = odds
                
        except Exception as e:
            logger.error(f"Error updating odds: {e}")
    
    async def fetch_odds(self, match_id: str) -> Dict:
        """Fetch odds for a specific match"""
        # TODO: Integrate with odds API (the-odds-api.com, betfair, etc.)
        return {
            'home': 2.10,
            'draw': 3.40,
            'away': 3.20,
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_odds_movement(self, old_odds: Dict, new_odds: Dict, threshold: float = 0.15) -> bool:
        """Detect significant odds movement (>15% change)"""
        for market in ['home', 'draw', 'away']:
            old_value = old_odds.get(market, 0)
            new_value = new_odds.get(market, 0)
            
            if old_value > 0:
                change_percent = abs((new_value - old_value) / old_value)
                if change_percent >= threshold:
                    return True
        
        return False
    
    async def check_alerts(self):
        """Check all active user alerts"""
        try:
            # Get all active alerts from database
            active_alerts = await self.get_active_alerts()
            
            for alert in active_alerts:
                if await self.evaluate_alert_condition(alert):
                    await self.trigger_user_alert(alert)
                    
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def get_active_alerts(self) -> List[Dict]:
        """Get all active user alerts from database"""
        # TODO: Implement database query
        return []
    
    async def evaluate_alert_condition(self, alert: Dict) -> bool:
        """Evaluate if alert condition is met"""
        alert_type = alert.get('type')
        match_id = alert.get('match_id')
        
        if alert_type == 'goal':
            match = self.active_matches.get(match_id)
            if match:
                total_goals = match.get('score_home', 0) + match.get('score_away', 0)
                return total_goals >= alert.get('min_goals', 1)
        
        elif alert_type == 'odds_threshold':
            odds = self.odds_history.get(match_id, {})
            target_team = alert.get('team', 'home')
            target_odds = alert.get('target_odds', 0)
            current_odds = odds.get(target_team, 0)
            return current_odds >= target_odds
        
        elif alert_type == 'match_start':
            match = self.active_matches.get(match_id)
            return match and match.get('status') == 'live'
        
        return False
    
    async def trigger_user_alert(self, alert: Dict):
        """Send alert notification to user"""
        user_id = alert.get('user_id')
        match_id = alert.get('match_id')
        match = self.active_matches.get(match_id, {})
        
        message = self.format_alert_message(alert, match)
        
        if self.bot:
            try:
                await self.bot.application.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
                # Mark alert as triggered
                await self.deactivate_alert(alert['id'])
                
            except Exception as e:
                logger.error(f"Failed to send alert to user {user_id}: {e}")
    
    def format_alert_message(self, alert: Dict, match: Dict) -> str:
        """Format alert message for user"""
        alert_type = alert.get('type')
        
        if alert_type == 'goal':
            return (
                f"🔔 **ALERT: Goal Scored!** ⚽\n"
                f"{match.get('home')} {match.get('score_home')} - "
                f"{match.get('score_away')} {match.get('away')}\n"
                f"⏱️ Minute: {match.get('minute')}'"
            )
        elif alert_type == 'odds_threshold':
            return (
                f"🔔 **ALERT: Odds Target Reached!** 📈\n"
                f"{match.get('home')} vs {match.get('away')}\n"
                f"Target odds: {alert.get('target_odds')}\n"
                f"Current odds: {self.odds_history.get(match.get('id'), {}).get(alert.get('team'), 'N/A')}"
            )
        elif alert_type == 'match_start':
            return (
                f"🔔 **ALERT: Match Started!** 🏁\n"
                f"{match.get('home')} vs {match.get('away')}\n"
                f"🏆 {match.get('league', 'Unknown League')}"
            )
        
        return "🔔 Your alert has been triggered!"
    
    async def deactivate_alert(self, alert_id: int):
        """Deactivate an alert after it's been triggered"""
        # TODO: Update database to mark alert as inactive
        pass
    
    async def update_statistics(self):
        """Update match statistics"""
        try:
            for match_id in self.active_matches.keys():
                stats = await self.fetch_match_stats(match_id)
                # Store stats in database
                # This can be used for in-play predictions
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
    
    async def fetch_match_stats(self, match_id: str) -> Dict:
        """Fetch detailed match statistics"""
        # TODO: Integrate with stats API
        return {
            'possession_home': 55,
            'possession_away': 45,
            'shots_home': 12,
            'shots_away': 8,
            'shots_on_target_home': 5,
            'shots_on_target_away': 3
        }
    
    async def update_inplay_predictions(self, match: Dict):
        """Update predictions based on current match state"""
        # TODO: Use ML model to generate in-play predictions
        pass
    
    async def scan_arbitrage(self):
        """Scan for arbitrage betting opportunities"""
        try:
            opportunities = []
            
            for match_id, match in self.active_matches.items():
                odds_data = await self.fetch_all_bookmaker_odds(match_id)
                
                if len(odds_data) >= 2:  # Need at least 2 bookmakers
                    arb = self.calculate_arbitrage(odds_data)
                    
                    if arb['is_opportunity']:
                        opportunities.append({
                            'match': match,
                            'arbitrage': arb
                        })
            
            # Notify premium users of arbitrage opportunities
            if opportunities:
                await self.notify_arbitrage_opportunities(opportunities)
                
        except Exception as e:
            logger.error(f"Error scanning arbitrage: {e}")
    
    async def fetch_all_bookmaker_odds(self, match_id: str) -> List[Dict]:
        """Fetch odds from multiple bookmakers"""
        # TODO: Integrate with multiple bookmaker APIs
        return [
            {'bookmaker': 'Bet365', 'home': 2.10, 'draw': 3.40, 'away': 3.20},
            {'bookmaker': 'William Hill', 'home': 2.15, 'draw': 3.30, 'away': 3.25},
        ]
    
    def calculate_arbitrage(self, odds_data: List[Dict]) -> Dict:
        """Calculate if there's an arbitrage opportunity"""
        best_home = max(o['home'] for o in odds_data)
        best_draw = max(o['draw'] for o in odds_data)
        best_away = max(o['away'] for o in odds_data)
        
        arbitrage_percent = (1/best_home + 1/best_draw + 1/best_away) * 100
        
        return {
            'is_opportunity': arbitrage_percent < 100,
            'profit_percent': 100 - arbitrage_percent if arbitrage_percent < 100 else 0,
            'best_home': best_home,
            'best_draw': best_draw,
            'best_away': best_away,
            'stakes': self.calculate_stakes(best_home, best_draw, best_away) if arbitrage_percent < 100 else None
        }
    
    def calculate_stakes(self, home_odds: float, draw_odds: float, away_odds: float, total_stake: float = 100) -> Dict:
        """Calculate optimal stake distribution for arbitrage"""
        sum_inverse = 1/home_odds + 1/draw_odds + 1/away_odds
        
        return {
            'home': round(total_stake / (home_odds * sum_inverse), 2),
            'draw': round(total_stake / (draw_odds * sum_inverse), 2),
            'away': round(total_stake / (away_odds * sum_inverse), 2)
        }
    
    async def notify_arbitrage_opportunities(self, opportunities: List[Dict]):
        """Notify premium users of arbitrage opportunities"""
        # Get premium/pro users from database
        premium_users = await self.get_premium_users()
        
        for user_id in premium_users:
            message = self.format_arbitrage_message(opportunities)
            try:
                await self.bot.application.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to notify user {user_id}: {e}")
    
    def format_arbitrage_message(self, opportunities: List[Dict]) -> str:
        """Format arbitrage opportunities message"""
        message = "💰 **ARBITRAGE OPPORTUNITIES DETECTED!** 💰\n\n"
        
        for opp in opportunities[:3]:  # Limit to top 3
            match = opp['match']
            arb = opp['arbitrage']
            
            message += (
                f"⚽ {match.get('home')} vs {match.get('away')}\n"
                f"💎 Profit: {arb['profit_percent']:.2f}%\n"
                f"📊 Best Odds: H {arb['best_home']} | D {arb['best_draw']} | A {arb['best_away']}\n"
                f"💰 Stakes: H ${arb['stakes']['home']} | D ${arb['stakes']['draw']} | A ${arb['stakes']['away']}\n\n"
            )
        
        return message
    
    async def get_premium_users(self) -> List[int]:
        """Get list of premium/pro users"""
        # TODO: Query database for premium users
        return []
    
    async def notify_score_change(self, new_match: Dict, old_match: Dict):
        """Notify users about score changes"""
        match_id = new_match['id']
        message = (
            f"⚽ **GOAL!** ⚽\n"
            f"{new_match['home']} {new_match['score_home']} - "
            f"{new_match['score_away']} {new_match['away']}\n"
            f"⏱️ {new_match['minute']}'\n"
            f"📈 Odds updating..."
        )
        
        # Get subscribed users
        subscribers = await self.get_match_subscribers(match_id)
        await self.broadcast_to_users(subscribers, message)
    
    async def notify_status_change(self, new_match: Dict, old_match: Dict):
        """Notify users about match status changes"""
        pass
    
    async def notify_match_started(self, match: Dict):
        """Notify users when a match starts"""
        pass
    
    async def handle_match_finished(self, match_id: str):
        """Handle match finish event"""
        pass
    
    async def notify_odds_change(self, match_id: str, old_odds: Dict, new_odds: Dict):
        """Notify users about significant odds changes"""
        pass
    
    async def get_match_subscribers(self, match_id: str) -> List[int]:
        """Get users subscribed to a match"""
        # TODO: Query database
        return []
    
    async def broadcast_to_users(self, user_ids: List[int], message: str):
        """Send message to multiple users"""
        for user_id in user_ids:
            try:
                await self.bot.application.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to notify user {user_id}: {e}")
    
    def stop(self):
        """Stop the live update service"""
        logger.info("🛑 Stopping Live Update Service...")
        self.scheduler.shutdown()
        logger.info("✅ Live Update Service stopped")


# Singleton instance
_live_service = None


def get_live_service(bot_instance=None, database=None):
    """Get or create live service instance"""
    global _live_service
    if _live_service is None:
        _live_service = LiveUpdateService(bot_instance, database)
    return _live_service
