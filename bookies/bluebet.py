import dacite
from models import BookieMatch, SCRAPING_TEMPLATE
from copy import deepcopy
from bs4 import BeautifulSoup
from datetime import datetime
from utils import standardise_team_name
import re

def extract_team_info(team_info_str):
    team_odds_regex = r"([a-zA-Z ]+)(\d+\.\d+)"
    match = re.match(team_odds_regex, team_info_str)
    if match:
        team = match.group(1)
        odds = float(match.group(2))
        return team, odds

def main(browser) -> list[BookieMatch]:
    print("Running bluebet script")

    page = browser.new_page()
    sports_links = {
        "afl": "https://www.bluebet.com.au/sports/Australian-Rules/101/AFL/Toyota-AFL-Premiership/43735" 
    }
    matches = []

    for sport, url in sports_links.items():
        page.goto(url) # Some selenium/playwright logic here
        soup = BeautifulSoup(page.content(), 'html.parser')

        match_elements = soup.find_all('div', attrs={'class': 'MuiCard-root'})
        
        # For each match in book, Deep Copy SCRAPING_TEMPLATE, fill it out and append to matches
        for match_element in match_elements:
            match = deepcopy(SCRAPING_TEMPLATE)
            match['bookie'] = 'bluebet'
            match['url'] = url
            match['sport'] = sport
            date = match_element.find_previous('h3', attrs={'class': 'MuiTypography-root'}).text.strip()
            match_header = match_element.find('div', attrs={'class': 'MuiCardContent-root'})
            time = match_header.find('div', attrs={'class': 'MuiTypography-caption'}).text.strip()
            match['date_time'] = datetime.strptime(f'{date} {time}', '%A %d/%m/%Y %H:%M') 

            match_body = match_element.find('div', attrs={'class': 'MuiCardActions-root'})
            team_info = match_body.find_all('button', attrs={'class': 'MuiButton-root'})
            team1, team1_odds = extract_team_info(team_info[0].text)
            team2, team2_odds = extract_team_info(team_info[1].text)
            match['team1'], match['team1_odds'] = standardise_team_name(sport, team1), team1_odds
            match['team2'], match['team2_odds'] = standardise_team_name(sport, team2), team2_odds
            match = dacite.from_dict(data_class=BookieMatch, data=match)
            matches.append(match)

    return matches