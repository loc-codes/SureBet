import dacite
from models import BookieMatch, SCRAPING_TEMPLATE
from config import MASTER_CONFIG
from copy import deepcopy
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils import standardise_team_name, round_to_nearest_five_minutes, standardise_today_tomorrow_date
import re

def standardise_countdown_information(time):
    regex = re.search(r"(\d+h)?\s*(\d+m)?\s*(\d+s)?", time)
    # Extract the matched groups
    hours = regex.group(1) if regex.group(1) else "0h"
    minutes = regex.group(2) if regex.group(2) else "0m"
    seconds = regex.group(3) if regex.group(3) else "0s"
    # Convert to integers
    hours = int(hours[:-1])  # remove the 'h' and convert to int
    minutes = int(minutes[:-1])  # remove the 'm' and convert to int
    # Calculate the new time
    current_time = datetime.now()
    time_difference = timedelta(hours=hours, minutes=minutes)
    new_time = (current_time + time_difference).time()
    time = new_time.strftime('%H:%M')
    return time

def extract_team_info(team_info_str):
    team_odds_regex = r"([a-zA-Z0-9. ]+)(\d+\.\d+)"
    match = re.match(team_odds_regex, team_info_str)
    if match:
        team = match.group(1)
        odds = float(match.group(2))
        return team, odds

def main(browser) -> list[BookieMatch]:
    print("Running bluebet script")
    bookie = 'bluebet'
    page = browser.new_page()
    config = MASTER_CONFIG[bookie]['sports']
    matches = []

    for sport, url in config.items():
        page.goto(url) 
        soup = BeautifulSoup(page.content(), 'html.parser')

        match_elements = soup.find_all('div', attrs={'class': 'MuiCard-root'})
        
        # For each match in book, Deep Copy SCRAPING_TEMPLATE, fill it out and append to matches
        for match_element in match_elements:
            match = deepcopy(SCRAPING_TEMPLATE)
            match['bookie'] = bookie
            match['url'] = url
            match['sport'] = sport
            date = match_element.find_previous('h3', attrs={'class': 'MuiTypography-root'}).text.strip()
            match_header = match_element.find('div', attrs={'class': 'MuiCardContent-root'})
            time = match_header.find('div', attrs={'class': 'MuiTypography-caption'}).text.strip()
            if "Today" in date or "Tomorrow" in date:
                date = standardise_today_tomorrow_date(date)
            if re.search(r"(\d+h)?\s*(\d+m)?\s*(\d+s)?", time):
                time = standardise_countdown_information(time)
            date_time = f'{date} {time}'
            match['date_time'] = round_to_nearest_five_minutes(datetime.strptime(date_time, "%A %d/%m/%Y %H:%M"))
            match_body = match_element.find('div', attrs={'class': 'MuiCardActions-root'})
            team_info = match_body.find_all('button', attrs={'class': 'MuiButton-root'})
            #print([team_inf.text for team_inf in team_info])
            team1, team1_odds = extract_team_info(team_info[0].text)
            team2, team2_odds = extract_team_info(team_info[1].text)
            #print(team2, team2_odds)
            match['team1'], match['team1_odds'] = standardise_team_name(sport, team1), team1_odds
            match['team2'], match['team2_odds'] = standardise_team_name(sport, team2), team2_odds
            match = dacite.from_dict(data_class=BookieMatch, data=match)
            matches.append(match)

    print("Finished bluebet script")
    return matches