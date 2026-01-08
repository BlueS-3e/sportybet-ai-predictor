"""
FastAPI Server for SportyBet AI Predictor
REST API with endpoints for predictions, hotpicks, and batch operations
"""
import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / 'ml-model'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'common'))
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

# Setup logging
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(log_dir / 'api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.warning("⚠️  FastAPI not available")

# Load canonical helpers
try:
    from prediction_utils import get_team_strength, predict_match
    from cache import PredictionCache
    CANONICAL_AVAILABLE = True
except ImportError:
    CANONICAL_AVAILABLE = False
    logger.warning("⚠️  Canonical helpers not available")

# Load ML model
try:
    from model import AdvancedMLModel
    ml_model = AdvancedMLModel()
    ML_MODEL_AVAILABLE = True
except ImportError:
    ml_model = None
    ML_MODEL_AVAILABLE = False
    logger.warning("⚠️  ML model not available")

# Initialize FastAPI
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="SportyBet AI Predictor API",
        description="AI-powered football prediction API",
        version="1.0.0"
    )
    
    # Initialize cache
    prediction_cache = PredictionCache(ttl_seconds=3600) if CANONICAL_AVAILABLE else None
    
    # Request/Response models
    class TeamStrengthRequest(BaseModel):
        team_name: str
    
    class PredictionRequest(BaseModel):
        home_team: str
        away_team: str
        league: Optional[str] = None
    
    class BatchPredictionRequest(BaseModel):
        matches: List[Dict]
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Check API health"""
        return {
            "status": "🟢 ONLINE",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "ml_model": "✅ Available" if ML_MODEL_AVAILABLE else "❌ Unavailable",
                "canonical_helpers": "✅ Available" if CANONICAL_AVAILABLE else "❌ Unavailable",
                "cache": "✅ Enabled" if prediction_cache else "❌ Disabled"
            }
        }
    
    # Prediction endpoints
    @app.post("/predict")
    async def predict(request: PredictionRequest):
        """Get match prediction"""
        cache_key = f"{request.home_team}_{request.away_team}"
        
        # Check cache
        if prediction_cache:
            cached = prediction_cache.get(cache_key)
            if cached:
                logger.debug(f"✅ Cache hit for {cache_key}")
                return {
                    "source": "cache",
                    "prediction": cached
                }
        
        # Get prediction
        try:
            if CANONICAL_AVAILABLE:
                result = predict_match(request.home_team, request.away_team)
            elif ML_MODEL_AVAILABLE:
                result = ml_model.predict_match({
                    'home_team': request.home_team,
                    'away_team': request.away_team,
                    'league': request.league
                })
            else:
                raise Exception("No prediction engine available")
            
            # Cache result
            if prediction_cache:
                prediction_cache.set(cache_key, result)
            
            return {
                "source": "model",
                "prediction": result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/predict/advanced")
    async def predict_advanced(request: PredictionRequest):
        """Get advanced prediction with analysis"""
        try:
            if ML_MODEL_AVAILABLE:
                prediction = ml_model.predict_match({
                    'home_team': request.home_team,
                    'away_team': request.away_team,
                    'league': request.league
                })
                
                analysis = ml_model.get_comprehensive_analysis(
                    request.home_team,
                    request.away_team,
                    league=request.league
                )
                
                return {
                    "prediction": prediction,
                    "analysis": analysis,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception("Advanced analysis not available")
        
        except Exception as e:
            logger.error(f"Advanced prediction error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/hotpicks")
    async def get_hotpicks():
        """Get today's hot picks"""
        try:
            if ML_MODEL_AVAILABLE:
                picks = ml_model.generate_hot_picks()
                return {
                    "hotpicks": picks,
                    "count": len(picks),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "hotpicks": [],
                    "count": 0,
                    "message": "Hot picks not available"
                }
        except Exception as e:
            logger.error(f"Hot picks error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/predict/batch")
    async def predict_batch(request: BatchPredictionRequest):
        """Batch prediction"""
        results = []
        
        for match in request.matches:
            try:
                home = match.get('home_team') or match.get('home')
                away = match.get('away_team') or match.get('away')
                
                if CANONICAL_AVAILABLE:
                    pred = predict_match(home, away)
                elif ML_MODEL_AVAILABLE:
                    pred = ml_model.predict_match(match)
                else:
                    pred = {"error": "No engine available"}
                
                results.append({
                    "match": f"{home} vs {away}",
                    "prediction": pred
                })
            
            except Exception as e:
                logger.error(f"Batch prediction error for {match}: {e}")
                results.append({
                    "match": str(match),
                    "error": str(e)
                })
        
        return {
            "total": len(results),
            "predictions": results,
            "timestamp": datetime.now().isoformat()
        }
    
    @app.post("/team/strength")
    async def get_team_strength_endpoint(request: TeamStrengthRequest):
        """Get team strength"""
        try:
            if CANONICAL_AVAILABLE:
                strength = get_team_strength(request.team_name)
            elif ML_MODEL_AVAILABLE:
                strength = ml_model._calculate_team_strength(request.team_name)
            else:
                strength = 0.5
            
            return {
                "team": request.team_name,
                "strength": strength,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Team strength error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


def main():
    """Run the API server"""
    if not FASTAPI_AVAILABLE:
        logger.error("❌ FastAPI not available. Install with: pip install fastapi uvicorn")
        sys.exit(1)
    
    import uvicorn
    
    port = int(os.getenv('API_PORT', 8000))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    logger.info(f"🚀 Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
