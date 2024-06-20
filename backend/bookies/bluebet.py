import dacite
from models import BookieMatch, SCRAPING_TEMPLATE
from config import MASTER_CONFIG
from copy import deepcopy
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils import standardise_team_name, round_to_nearest_five_minutes
import re

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
            date_time = f'{date} {time}'
            if "Today" in date:
                # Example Edge Case: Today 20/06/2024 -02h 04m
                today_date = datetime.now()
                time_str = time_str.replace("Today", today_date.strftime("%A %d/%m/%Y"))

                # Extract hours and minutes
                time_offset = time_str.split(' ')[-1]  # Extract '-02h 04m'
                hours_offset = int(time_offset.split('h')[0])
                minutes_offset = int(time_offset.split('h ')[1].replace('m', ''))
                # Add hours and minutes to the current time
                date_time = today_date + timedelta(hours=hours_offset, minutes=minutes_offset)
            elif "Tomorrow" in date:
                tomorrow_date = datetime.now() + timedelta(days=1)
                date = date.replace("Tomorrow", tomorrow_date.strftime("%A"))
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

    return matches