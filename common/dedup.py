"""
Match deduplication utilities
"""
from typing import List, Dict, Set


def deduplicate_matches(matches: List[Dict]) -> List[Dict]:
    """Remove duplicate matches from a list"""
    seen: Set[str] = set()
    deduplicated = []
    
    for match in matches:
        # Create a unique key from match details
        home_team = str(match.get('home_team', '')).lower().strip()
        away_team = str(match.get('away_team', '')).lower().strip()
        match_date = str(match.get('date', match.get('utcDate', ''))).split('T')[0]
        
        key = f"{home_team}_{away_team}_{match_date}"
        
        if key not in seen:
            seen.add(key)
            deduplicated.append(match)
    
    return deduplicated
