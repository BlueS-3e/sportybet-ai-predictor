"""
Football Team Searcher
Fuzzy matching and team lookup utility
"""
import logging
from typing import List, Tuple, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class FootballTeamSearcher:
    """Find and match football teams by name"""
    
    # Known teams across major leagues
    KNOWN_TEAMS = {
        # Premier League
        'manchester city': ['Man City', 'Man. City', 'MCFC'],
        'manchester united': ['Man Utd', 'Man. Utd', 'MUFC'],
        'arsenal': ['AFC'],
        'liverpool': ['LFC'],
        'chelsea': ['CFC'],
        'tottenham': ['Spurs', 'Tottenham Hotspur'],
        'newcastle': ['NUFC'],
        'aston villa': ['Villa'],
        'brighton': ['Brighton & Hove Albion'],
        'bournemouth': ['AFC Bournemouth'],
        'west ham': ['West Ham United', 'WHUFC'],
        'everton': ['EFC'],
        'fulham': ['FFC'],
        'crystal palace': ['CPFC'],
        'ipswich': ['Ipswich Town'],
        'leicester': ['Leicester City', 'LCFC'],
        'coventry': ['Coventry City'],
        'wolves': ['Wolverhampton', 'Wolves'],
        'nottingham forest': ['Nottm Forest', 'NFFC'],
        'southampton': ['Saints'],
        
        # La Liga
        'real madrid': ['RM'],
        'barcelona': ['Barça', 'FC Barcelona', 'FCB'],
        'atletico madrid': ['Atlético Madrid'],
        'sevilla': ['Sevilla FC'],
        'valencia': ['Valencia CF'],
        'villarreal': ['Villarreal CF'],
        'real sociedad': ['Real Sociedad'],
        'athletic bilbao': ['Ath. Bilbao', 'Athletic'],
        'betis': ['Real Betis'],
        'celta vigo': ['Celta'],
        
        # Serie A
        'juventus': ['Juve', 'Juventus'],
        'inter': ['Inter Milan', 'Internazionale'],
        'ac milan': ['Milan', 'AC Milan'],
        'roma': ['AS Roma'],
        'lazio': ['SS Lazio'],
        'napoli': ['Napoli FC'],
        'atalanta': ['Atalanta BC'],
        'fiorentina': ['ACF Fiorentina'],
        'torino': ['Torino FC'],
        'sassuolo': ['US Sassuolo'],
        
        # Bundesliga
        'bayern munich': ['Bayern', 'FCB'],
        'borussia dortmund': ['Dortmund', 'BVB'],
        'bayer leverkusen': ['Leverkusen'],
        'rb leipzig': ['RB Leipzig', 'Leipzig'],
        'borussia monchengladbach': ['Borussia M\'gladbach', 'Gladbach'],
        'schalke': ['Schalke 04'],
        'cologne': ['Cologne'],
        'frankfurt': ['Eintracht Frankfurt'],
        'hamburg': ['Hamburger SV', 'Hamburg'],
        'berlin': ['Hertha Berlin'],
        
        # Ligue 1
        'psg': ['PSG', 'Paris Saint-Germain', 'Paris SG'],
        'marseille': ['Olympique Marseille', 'OM'],
        'monaco': ['AS Monaco'],
        'lyon': ['Olympique Lyonnais', 'OL'],
        'lens': ['RC Lens'],
        'rennes': ['Stade Rennes'],
        'nice': ['OGC Nice', 'Nice'],
        'toulouse': ['Toulouse FC'],
        'strasbourg': ['RC Strasbourg'],
        'nantes': ['FC Nantes']
    }
    
    def __init__(self):
        """Initialize searcher"""
        logger.info("🔍 Football team searcher initialized")
    
    def find_team(self, query: str, threshold: float = 0.6) -> Optional[str]:
        """
        Find team matching query
        
        Args:
            query: Team name query
            threshold: Similarity threshold (0-1)
        
        Returns:
            Canonical team name if found
        """
        query_lower = query.lower().strip()
        
        # Direct match
        if query_lower in self.KNOWN_TEAMS:
            return query_lower
        
        # Check aliases
        for canonical, aliases in self.KNOWN_TEAMS.items():
            for alias in aliases:
                if alias.lower() == query_lower:
                    return canonical
        
        # Fuzzy match
        best_match = None
        best_score = threshold
        
        for canonical in self.KNOWN_TEAMS.keys():
            score = SequenceMatcher(None, query_lower, canonical).ratio()
            if score > best_score:
                best_score = score
                best_match = canonical
        
        return best_match
    
    def search_teams(self, query: str, limit: int = 5) -> List[Tuple[str, float]]:
        """
        Search for teams matching query
        
        Args:
            query: Search query
            limit: Max results
        
        Returns:
            List of (team_name, similarity_score) tuples
        """
        query_lower = query.lower().strip()
        results = []
        
        for canonical in self.KNOWN_TEAMS.keys():
            score = SequenceMatcher(None, query_lower, canonical).ratio()
            if score > 0.5:
                results.append((canonical, score))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def validate_team(self, team_name: str) -> bool:
        """Check if team is known"""
        return self.find_team(team_name) is not None
    
    def get_team_aliases(self, team_name: str) -> List[str]:
        """Get all aliases for a team"""
        canonical = self.find_team(team_name)
        if canonical and canonical in self.KNOWN_TEAMS:
            return [canonical] + self.KNOWN_TEAMS[canonical]
        return []
    
    def normalize_team_name(self, team_name: str) -> Optional[str]:
        """Normalize team name to canonical form"""
        return self.find_team(team_name)


# Global instance
_searcher = None


def get_team_searcher() -> FootballTeamSearcher:
    """Get or create team searcher"""
    global _searcher
    if _searcher is None:
        _searcher = FootballTeamSearcher()
    return _searcher
