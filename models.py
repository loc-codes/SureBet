# templates.py

from dataclasses import dataclass, field
from utils import round_to_nearest_5
from config import BET_SIZE
from datetime import datetime

@dataclass
class Match:
    date_time: datetime
    sport: str
    team1: str
    team2: str

@dataclass
class BookieMatch(Match):
    bookie: str
    url: str
    team1_odds: float
    team2_odds: float

@dataclass
class TeamMax:
    bookie: str
    odds: float
    url: str

@dataclass
class ArbitrageInfo:
    team1_residual: float
    team2_residual: float
    team1_max: TeamMax
    team2_max: TeamMax
    coefficient: float
    team1_weight: int = field(init=False)
    team2_weight: int = field(init=False)
    team1_ev: float = field(init=False)
    team2_ev: float = field(init=False)
    arbitrage_ev: float = field(init=False)
    team1_profit: float = field(init=False)
    team2_profit: float = field(init=False)
    arbitrage_profit: float = field(init=False)
    executable_arb: bool = field(init=False)
    zero_loss_arb: bool = field(init=False)

    def __post_init__(self):
        self.team1_weight = round_to_nearest_5(self.team1_residual / self.coefficient)
        self.team2_weight = round_to_nearest_5(self.team2_residual / self.coefficient)
        self.team1_ev = self.team1_weight * self.team1_max.odds
        self.team2_ev = self.team2_weight * self.team2_max.odds
        self.arbitrage_ev = (self.team1_ev + self.team2_ev) / 2 - 1
        team1_revenue = self.team1_ev * BET_SIZE
        team2_revenue = self.team2_ev * BET_SIZE
        self.arbitrage_profit = (team1_revenue + team2_revenue) / 2 - BET_SIZE
        self.team1_profit = team1_revenue - BET_SIZE
        self.team2_profit = team2_revenue - BET_SIZE
        self.executable_arb = self.arbitrage_ev > 1
        self.zero_loss_arb = self.executable_arb and self.team1_ev > 1 and self.team2_ev > 1

@dataclass
class MasterMatch(Match):
    team1_max: TeamMax = field(init=False)
    team2_max: TeamMax = field(init=False)
    coefficient: float = field(init=False)
    # arbitrage_info: ArbitrageInfo = field(init=False)

    def __init__(self, bookie_match1: BookieMatch, bookie_match2: BookieMatch):
        if check_bookie_matches(bookie_match1, bookie_match2):
            super().__init__(bookie_match1.date_time, bookie_match1.sport, bookie_match1.team1, bookie_match1.team2)
            self.team1_max = TeamMax(bookie=bookie_match1.bookie, odds=bookie_match1.team1_odds, url=bookie_match1.url)
            self.team2_max = TeamMax(bookie=bookie_match2.bookie, odds=bookie_match2.team2_odds, url=bookie_match2.url)
            self.generate_arb_info()

    def generate_arb_info(self):
        team1_residual = 1 / self.team1_max.odds
        team2_residual = 1 / self.team2_max.odds
        self.coefficient = team1_residual + team2_residual
        if self.coefficient < 1:
            self.arbitrage_info = ArbitrageInfo(team1_residual=team1_residual, team2_residual=team2_residual, team1_max=self.team1_max, team2_max=self.team2_max, coefficient=self.coefficient)

SCRAPING_TEMPLATE = {
    "date_time": "",    # Example: "2024-06-17 10:00:00"
    "sport": "",        # Example: "AFL"
    "team1": "",        # Example: "Team A"
    "team2": "",        # Example: "Team B"
    "bookie": "",       # Example: "BookieX"
    "url": "",         # Example: "http://example.com"
    "team1_odds": 1.01, # Example: 1.5
    "team2_odds": 1.01  # Example: 2.5
}

def check_bookie_matches(bookie_match1: BookieMatch, bookie_match2: BookieMatch) -> bool:
    teams_match = bookie_match1.team1 == bookie_match2.team1 and bookie_match1.team2 == bookie_match2.team2
    sports_match = bookie_match1.sport == bookie_match2.sport
    dates_match = bookie_match1.date_time == bookie_match2.date_time
    if teams_match and sports_match and dates_match:
        return True
    return False