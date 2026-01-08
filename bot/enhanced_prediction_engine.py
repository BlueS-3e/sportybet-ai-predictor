"""
Enhanced Prediction Engine
Provides advanced prediction capabilities with multiple analysis methods
"""
import logging
import asyncio
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class EnhancedPredictionEngine:
    """Advanced prediction engine with multiple analysis methods"""
    
    def __init__(self, use_canonical=True):
        """Initialize prediction engine"""
        self.use_canonical = use_canonical
        self.ml_model = None
        self.canonical_predict = None
        
        # Try loading ML model
        try:
            from model import AdvancedMLModel
            self.ml_model = AdvancedMLModel()
            logger.info("✅ ML Model loaded in prediction engine")
        except ImportError:
            logger.warning("⚠️  ML Model not available in prediction engine")
        
        # Try loading canonical helpers
        if use_canonical:
            try:
                from prediction_utils import predict_match as canonical_predict
                self.canonical_predict = canonical_predict
                logger.info("✅ Canonical prediction helpers loaded")
            except ImportError:
                logger.warning("⚠️  Canonical helpers not available")
    
    def _normalize_canonical_prediction(self, result: Dict) -> Dict:
        """Normalize canonical prediction format"""
        if not result:
            return self._default_prediction()
        
        probs = result.get('probabilities', {})
        return {
            'home_win_prob': probs.get('home', 0.33),
            'draw_prob': probs.get('draw', 0.34),
            'away_win_prob': probs.get('away', 0.33),
            'confidence': result.get('confidence', 0.5),
            'recommended_bet': result.get('recommended_bet', 'Draw'),
            'analysis': 'Canonical ML-based prediction'
        }
    
    def _default_prediction(self) -> Dict:
        """Return default prediction when models unavailable"""
        return {
            'home_win_prob': 0.40,
            'draw_prob': 0.30,
            'away_win_prob': 0.30,
            'confidence': 0.5,
            'recommended_bet': 'Draw',
            'analysis': 'Conservative default prediction'
        }
    
    async def predict_match(self, home_team: str, away_team: str, 
                           match_data: Optional[Dict] = None) -> Dict:
        """
        Predict match outcome with multiple analysis methods
        
        Args:
            home_team: Home team name
            away_team: Away team name
            match_data: Optional match data (date, league, etc)
        
        Returns:
            Prediction dict with probabilities, confidence, recommendation
        """
        # Try canonical prediction first
        if self.use_canonical and self.canonical_predict:
            try:
                result = self.canonical_predict(home_team, away_team)
                normalized = self._normalize_canonical_prediction(result)
                logger.debug(f"✅ Canonical prediction for {home_team} vs {away_team}")
                return normalized
            except Exception as e:
                logger.warning(f"⚠️  Canonical prediction failed: {e}")
        
        # Fall back to ML model
        if self.ml_model:
            try:
                match_dict = match_data or {
                    'home_team': home_team,
                    'away_team': away_team
                }
                result = self.ml_model.predict_match(match_dict)
                logger.debug(f"✅ ML model prediction for {home_team} vs {away_team}")
                return result
            except Exception as e:
                logger.warning(f"⚠️  ML model prediction failed: {e}")
        
        # Return default
        logger.warning(f"⚠️  Using default prediction for {home_team} vs {away_team}")
        return self._default_prediction()
    
    async def generate_enhanced_prediction(self, home_team: str, away_team: str, 
                                          include_analysis: bool = True) -> Dict:
        """
        Generate enhanced prediction with detailed analysis
        
        Args:
            home_team: Home team name
            away_team: Away team name
            include_analysis: Whether to include detailed analysis
        
        Returns:
            Enhanced prediction with analysis
        """
        base_prediction = await self.predict_match(home_team, away_team)
        
        if not include_analysis:
            return base_prediction
        
        # Add analysis components
        enhanced = {
            **base_prediction,
            'team_comparison': self._analyze_team_comparison(home_team, away_team),
            'statistical_indicators': self._get_statistical_indicators(
                home_team, away_team
            ),
            'risk_assessment': self._assess_risk(base_prediction)
        }
        
        return enhanced
    
    def _analyze_team_comparison(self, home_team: str, away_team: str) -> Dict:
        """Analyze teams for comparison"""
        # Get team strengths if model available
        if self.ml_model:
            try:
                home_strength = self.ml_model._calculate_team_strength(home_team)
                away_strength = self.ml_model._calculate_team_strength(away_team)
                
                return {
                    'home_team_strength': home_strength,
                    'away_team_strength': away_strength,
                    'strength_difference': home_strength - away_strength,
                    'home_advantage_factor': 0.08
                }
            except Exception:
                pass
        
        return {
            'home_team_strength': 0.5,
            'away_team_strength': 0.5,
            'strength_difference': 0.0,
            'home_advantage_factor': 0.08
        }
    
    def _get_statistical_indicators(self, home_team: str, away_team: str) -> Dict:
        """Get statistical indicators"""
        return {
            'possession_tendency': 'Even',
            'expected_goals_home': 1.5,
            'expected_goals_away': 1.2,
            'defensive_strength_home': 'Medium',
            'defensive_strength_away': 'Medium',
            'recent_form_home': 'Good',
            'recent_form_away': 'Average'
        }
    
    def _assess_risk(self, prediction: Dict) -> Dict:
        """Assess prediction risk level"""
        confidence = prediction.get('confidence', 0.5)
        
        if confidence > 0.75:
            risk = 'Low'
        elif confidence > 0.60:
            risk = 'Medium'
        else:
            risk = 'High'
        
        return {
            'risk_level': risk,
            'confidence_score': int(confidence * 100),
            'variance': 1.0 - confidence,
            'recommended_stake': 'Conservative' if risk == 'High' else 'Moderate'
        }
    
    def predict_multiple(self, matches: list) -> list:
        """Predict multiple matches"""
        predictions = []
        
        for match in matches:
            try:
                home = match.get('home_team') or match.get('home')
                away = match.get('away_team') or match.get('away')
                
                pred = asyncio.run(self.predict_match(home, away, match))
                predictions.append({
                    'match': f"{home} vs {away}",
                    'prediction': pred
                })
            except Exception as e:
                logger.error(f"Error predicting {match}: {e}")
        
        return predictions
    
    def batch_predict(self, home_teams: list, away_teams: list) -> Dict:
        """Batch predict from teams lists"""
        if len(home_teams) != len(away_teams):
            raise ValueError("home_teams and away_teams must have same length")
        
        predictions = {}
        for i, (home, away) in enumerate(zip(home_teams, away_teams)):
            key = f"{home}_vs_{away}"
            try:
                pred = asyncio.run(self.predict_match(home, away))
                predictions[key] = pred
            except Exception as e:
                logger.error(f"Batch prediction error for {home} vs {away}: {e}")
                predictions[key] = self._default_prediction()
        
        return predictions


# Global engine instance
_engine_instance = None


def get_prediction_engine(use_canonical=True) -> EnhancedPredictionEngine:
    """Get or create prediction engine"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = EnhancedPredictionEngine(use_canonical=use_canonical)
    return _engine_instance
