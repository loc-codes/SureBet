# config.py
BOOKIES = []
SPORTS = [] # Pulled from master sports list
BET_SIZE = 100

MASTER_CONFIG = {
    "sportsbet": {
        "sports": {
            "afl": "https://www.sportsbet.com.au/betting/australian-rules",
            #"nba": "https://www.sportsbet.com.au/betting/basketball-us/nba",
            "mlb": "https://www.sportsbet.com.au/betting/baseball",
            #"nhl": "https://www.sportsbet.com.au/betting/ice-hockey-us/nhl-games"
        }
    },
    "bluebet": {
        "sports": {
            "afl": "https://www.bluebet.com.au/sports/Australian-Rules/101",
            #"nba": "https://www.bluebet.com.au/sports/Basketball/107",
            "mlb": "https://www.bluebet.com.au/sports/Baseball/103",
            #"nhl": "https://www.bluebet.com.au/sports/Ice-Hockey/111"
        }
    },
    "neds": {
        "sports": {
            "afl": "https://www.neds.com.au/sports/australian-rules/afl",
            #"nba": "https://www.neds.com.au/sports/basketball/nba",
            "mlb": "https://www.neds.com.au/sports/baseball/mlb",
            #"nhl": "https://www.neds.com.au/sports/ice-hockey/usa/nhl",
        }
    },
    "playup": {
        "sports": {
            "afl": "https://www.playup.com.au/betting/sports/australian-rules/afl",
            #"nba": "https://www.playup.com.au/betting/sports/basketball/nba",
            "mlb": "https://www.playup.com.au/betting/sports/baseball/mlb",
            #"nhl": "https://www.playup.com.au/betting/sports/ice-hockey/nhl"
        }
    },
    "unibet": {
        "sports": {
            "afl": "https://www.unibet.com.au/betting/sports/filter/australian_rules/all/matches",
            #"nba": "https://www.unibet.com.au/betting/sports/filter/basketball/nba/all/matches",
            "mlb": "https://www.unibet.com.au/betting/sports/filter/baseball/mlb/all/matches",
            # NO NHL FOR UNIBET, THEY OFFER DRAWS "nhl": "https://www.unibet.com.au/betting/sports/filter/ice_hockey/nhl/all/matches"
        }
    },
}