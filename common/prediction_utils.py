"""
Canonical prediction utilities with fallback support

These wrappers delegate to the AdvancedMLModel when available.
Falls back to conservative defaults if the model is unavailable.
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

_ML_MODEL = None


def _get_ml_model():
    """Get the ML model instance"""
    global _ML_MODEL
    if _ML_MODEL is not None:
        return _ML_MODEL

    try:
        from model import AdvancedMLModel
        _ML_MODEL = AdvancedMLModel()
        return _ML_MODEL
    except Exception as e:
        logger.debug(f"AdvancedMLModel not available: {e}")
        return None


def get_team_strength(team_name: str) -> float:
    """Return normalized team strength (0.0-1.0)"""
    model = _get_ml_model()
    try:
        if model is not None:
            return float(model._calculate_team_strength(team_name))
    except Exception:
        logger.debug("Model calculation failed, using fallback")

    if not team_name:
        return 0.65
    return 0.65


def get_team_form(team_name: str) -> float:
    """Return recent form factor for the team (0.0-1.0)"""
    model = _get_ml_model()
    try:
        if model is not None:
            return float(model.get_team_form(team_name))
    except Exception:
        logger.debug("Model form calculation failed, using fallback")

    return 0.5


def predict_match(home_team: str, away_team: str) -> Dict:
    """Return prediction dict for a match"""
    model = _get_ml_model()
    if model is not None:
        try:
            return model.predict_match({"home_team": home_team, "away_team": away_team})
        except Exception as e:
            logger.error(f"Model prediction failed: {e}")

    # Lightweight fallback prediction
    home_strength = get_team_strength(home_team)
    away_strength = get_team_strength(away_team)
    home_adv = 0.08
    diff = home_strength - away_strength + home_adv

    if diff > 0.15:
        home_prob = 0.5
        draw_prob = 0.25
        away_prob = 0.25
    elif diff < -0.15:
        away_prob = 0.5
        draw_prob = 0.25
        home_prob = 0.25
    else:
        home_prob = 0.38
        draw_prob = 0.27
        away_prob = 0.35

    total = home_prob + draw_prob + away_prob
    home_prob /= total
    draw_prob /= total
    away_prob /= total

    confidence = min(0.95, 0.6 + (max(home_prob, draw_prob, away_prob) - min(home_prob, draw_prob, away_prob)) * 0.7)

    return {
        "probabilities": {
            "home": round(home_prob, 3),
            "draw": round(draw_prob, 3),
            "away": round(away_prob, 3)
        },
        "odds": {
            "home": round(1 / home_prob, 2) if home_prob > 0 else 10.0,
            "draw": round(1 / draw_prob, 2) if draw_prob > 0 else 10.0,
            "away": round(1 / away_prob, 2) if away_prob > 0 else 10.0
        },
        "confidence": round(confidence, 3),
        "recommended_bet": "home" if home_prob > max(draw_prob, away_prob) else ("away" if away_prob > draw_prob else "draw")
    }
