# utils.py
from models import BookieMatch
from dataclasses import dataclass, asdict

def round_to_nearest_5(value):
    return round(value / 5) * 5

def check_bookie_matches(bookie_match1: BookieMatch, bookie_match2: BookieMatch) -> bool:
    teams_match = bookie_match1.team1 == bookie_match2.team1 and bookie_match1.team2 == bookie_match2.team2
    sports_match = bookie_match1.sport == bookie_match2.sport
    dates_match = bookie_match1.date_time == bookie_match2.date_time
    if teams_match and sports_match and dates_match:
        return True
    return False