"""
This script is designed to scrape sports match data from Sportsbet.
It identifies and processes two types of match elements on the webpage:
- Type 1: Elements with data-automation-id "multi-market-coupon-event", which are easier to scrape and commonly used for popular sports.
- Type 2: Elements with data-automation-id "competition-event-card", which require additional handling as the date is stored outside the main match element.
"""


import dacite
from models import BookieMatch, SCRAPING_TEMPLATE
from config import MASTER_CONFIG
from copy import deepcopy
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils import standardise_team_name, round_to_nearest_five_minutes
import re

def handle_sportsbet_team_names(team):
    # Built mainly to handle baseball names like Detroit Tigers (T Skubal)
    team = team.split('(')[0].strip()
    return team

def extract_match_element_type_1_odds(match_element):
    # Scrape the odds under 'Head to Head'
    head_to_head_section = match_element.find_next('div', class_='market-coupon-col-0')
    price_buttons = head_to_head_section.find_all('div', attrs={'data-automation-id': 'multi-market-sports-outcome-button'})
    odds = [button.find('span', attrs={'data-automation-id': 'price-text'}).get_text() for button in price_buttons]
    team1_odds, team2_odds = float(odds[0]), float(odds[1])
    return team1_odds, team2_odds

def main(browser) -> list[BookieMatch]:
    print("Running sportsbet script")

    bookie = 'sportsbet'
    page = browser.new_page()
    config = MASTER_CONFIG[bookie]['sports']
    matches = []

    for sport, url in config.items():
        page.goto(url) 
        soup = BeautifulSoup(page.content(), 'html.parser')

        match_elements_type_1 = soup.find_all('div', attrs={'data-automation-id': 'multi-market-coupon-event'})
        match_elements_type_2 = [] # TO DO: add support for competition event card
        
        # For each match in book, Deep Copy SCRAPING_TEMPLATE, fill it out and append to matches
        for match_element in match_elements_type_1:
            match = deepcopy(SCRAPING_TEMPLATE)
            match['bookie'] = 'sportsbet'
            match['url'] = url
            match['sport'] = sport
            team1 = match_element.find('div', attrs={'data-automation-id': 'participant-one'}).text
            team2 = match_element.find('div', attrs={'data-automation-id': 'participant-two'}).text
            team1, team2 = handle_sportsbet_team_names(team1), handle_sportsbet_team_names(team2)
            team1, team2 = standardise_team_name(sport, team1), standardise_team_name(sport, team2)
            match['team1'], match['team2'] = team1, team2
            if sport == 'mlb':
                match['team1'], match['team2'] = team2, team1 # Sportsbet changes order of home and away teams
            date = match_element.find_previous('div', attrs={'data-automation-id': 'competition-event-group-title'}).text
            time = match_element.find('span', attrs={'data-automation-id': 'competition-event-card-time'}).text
            time = re.match(r"(\d{1,2}:\d{2})", time).group(1)
            # This could cause fake negatives - known bug to fix
            date_time = f'{date} {time} {datetime.now().year}'
            if "Tomorrow" in date_time:
                tomorrow_date = datetime.now() + timedelta(days=1)
                date_time = date_time.replace("Tomorrow", f'{tomorrow_date.strftime("%A")},')
            date_time = datetime.strptime(date_time, "%A, %d %b %H:%M %Y")
            match['date_time'] = round_to_nearest_five_minutes(date_time)
            team1_odds, team2_odds = extract_match_element_type_1_odds(match_element)
            match['team1_odds'], match['team2_odds'] = team1_odds, team2_odds
            if sport == 'mlb':
                 match['team1_odds'], match['team2_odds'] = team2_odds, team1_odds # Sportsbet changes order of home and away teams
            match = dacite.from_dict(data_class=BookieMatch, data=match)
            matches.append(match)

        for match_element in match_elements_type_2:
            match = deepcopy(SCRAPING_TEMPLATE)
            # TO DO: Add support for competitition event card

            # END TO DO
            match = dacite.from_dict(data_class=BookieMatch, data=match)
            matches.append(match)

    print("Finished sportsbet script")
    return matches
