"""
Test script to demonstrate enhanced AI model capabilities
"""
import sys
from pathlib import Path

# Add ml-model to path
sys.path.insert(0, str(Path(__file__).parent / 'ml-model'))

from model import AdvancedMLModel

def test_enhanced_model():
    """Test the enhanced AI model"""
    print("\n" + "="*70)
    print("🤖 TESTING ENHANCED AI MODEL")
    print("="*70 + "\n")
    
    model = AdvancedMLModel()
    
    # Test matches
    test_matches = [
        ("Manchester City", "Arsenal"),
        ("Real Madrid", "Barcelona"),
        ("Bayern Munich", "Borussia Dortmund"),
        ("Liverpool", "Chelsea"),
        ("Inter", "Napoli"),
    ]
    
    for home, away in test_matches:
        print(f"\n📊 MATCH: {home} vs {away}")
        print("-" * 70)
        
        prediction = model.predict_match({
            "home_team": home,
            "away_team": away
        })
        
        # Display results
        probs = prediction['probabilities']
        print(f"🎯 Prediction: {prediction['prediction']}")
        print(f"✅ Confidence: {prediction['confidence']*100:.1f}%")
        print(f"\n📈 Win Probabilities:")
        print(f"   Home: {probs['home']*100:.1f}% (Odds: {prediction['odds']['home']:.2f})")
        print(f"   Draw: {probs['draw']*100:.1f}% (Odds: {prediction['odds']['draw']:.2f})")
        print(f"   Away: {probs['away']*100:.1f}% (Odds: {prediction['odds']['away']:.2f})")
        
        print(f"\n⚽ Expected Goals: {prediction['expected_goals']['home']:.2f} - {prediction['expected_goals']['away']:.2f}")
        
        print(f"\n🏆 Elo Ratings:")
        print(f"   {home}: {prediction['elo_ratings']['home']}")
        print(f"   {away}: {prediction['elo_ratings']['away']}")
        
        print(f"\n📊 Form Factors:")
        print(f"   {home}: {prediction['form_factors']['home']:.2f}")
        print(f"   {away}: {prediction['form_factors']['away']:.2f}")
        
        print(f"\n💡 Recommended Bet: {prediction['recommended_bet'].upper()}")
        print(f"📝 Analysis: {prediction['analysis']}")
        
        if prediction.get('value_bets'):
            print(f"\n💰 Value Bets Detected:")
            for vb in prediction['value_bets']:
                print(f"   {vb['outcome'].upper()}: {vb['edge']}% edge")
    
    # Test hot picks
    print("\n\n" + "="*70)
    print("🔥 TODAY'S HOT PICKS")
    print("="*70 + "\n")
    
    hot_picks = model.generate_hot_picks()
    for i, pick in enumerate(hot_picks, 1):
        print(f"{i}. {pick['match']}")
        print(f"   Prediction: {pick['prediction']}")
        print(f"   Confidence: {pick['confidence']*100:.1f}%")
        print(f"   Expected Score: {pick['expected_goals']}")
        print(f"   Fair Odds: {pick['odds']:.2f}")
        print(f"   Reason: {pick['reason']}")
        print()
    
    print("="*70)
    print("✅ ENHANCED MODEL TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_enhanced_model()
