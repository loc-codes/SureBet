# utils.py
from datetime import datetime, timedelta
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

def round_to_nearest_five_minutes(date_time: datetime):
    '''
    Sportsbet often has matches 1 minute later than others
    '''    
    # Calculate the number of minutes since the start of the hour
    minutes = date_time.minute
    remainder = minutes % 5
    if remainder >= 2.5:
        rounded_minutes = minutes + (5 - remainder)
    else:
        rounded_minutes = minutes - remainder
    rounded_date_time = date_time.replace(minute=0) + timedelta(minutes=rounded_minutes)
    
    return rounded_date_time

def standardise_today_tomorrow_date(date, format="day only"):
    today_date, tomorrow_date = datetime.now(), datetime.now() + timedelta(days=1)
    if format == "day only":
        date = date.replace("Today", today_date.strftime("%A"))
        date = date.replace("Tomorrow", tomorrow_date.strftime("%A"))
    elif format == "day month year":
        date = date.replace("Today", today_date.strftime("%d %B %Y"))
        date = date.replace("Tomorrow", tomorrow_date.strftime("%d %B %Y"))
    return date