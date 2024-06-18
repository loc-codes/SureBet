# utils.py
from datetime import datetime
from mappings import team_names

def round_to_nearest_5(value):
    return round(value / 5) * 5

def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def standardise_team_name(sport, team):
    team = team_names[sport][team]
    return team