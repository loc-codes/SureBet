

import dacite
from models import BookieMatch, SCRAPING_TEMPLATE
from copy import deepcopy
from bs4 import BeautifulSoup
from datetime import datetime
from utils import standardise_team_name
import re

def neds_extract_team_info(team_info_element):
    team = team_info_element.find('div', attrs={'class': 'price-button-name'}).text
    odds = float(team_info_element.find('div', attrs={'class': 'price-button-odds-price'}).text)
    return team, odds

def main(browser) -> list[BookieMatch]:
    print("Running neds script")

    page = browser.new_page()
    sports_links = {
        "afl": "https://www.neds.com.au/sports/australian-rules/afl" 
    }
    matches = []

    for sport, url in sports_links.items():
        page.goto(url) # Some selenium/playwright logic here
        soup = BeautifulSoup(page.content(), 'html.parser')

        match_elements = soup.find_all('div', attrs={'class': "sport-event-card"})
        
        # For each match in book, Deep Copy SCRAPING_TEMPLATE, fill it out and append to matches
        for match_element in match_elements:
            match = deepcopy(SCRAPING_TEMPLATE)
            match['bookie'] = 'neds'
            match['url'] = url
            match['sport'] = sport

            date = match_element.find_previous('div', attrs={'class': 'sports-date-title'}).text.strip()
            time = match_element.find('span', attrs={'class': 'sport-event-card__countdown'}).text.strip()
            match['date_time'] = datetime.strptime(f'{date} {time}', "%A %d/%m/%Y %I:%M%p")
         
            team_info = match_element.find_all('div', attrs={'class': 'price-button-simple'})
            team1, team1_odds = neds_extract_team_info(team_info[0])
            team2, team2_odds = neds_extract_team_info(team_info[1])
            match['team1'], match['team1_odds'] = standardise_team_name(sport, team1), team1_odds
            match['team2'], match['team2_odds'] = standardise_team_name(sport, team2), team2_odds
            match = dacite.from_dict(data_class=BookieMatch, data=match)
            matches.append(match)

    return matches