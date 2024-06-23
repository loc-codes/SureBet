

import dacite
from models import BookieMatch, SCRAPING_TEMPLATE
from config import MASTER_CONFIG
from copy import deepcopy
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils import standardise_team_name, round_to_nearest_five_minutes, standardise_today_tomorrow_date
from time import sleep

def main(browser) -> list[BookieMatch]:
    print("Running unibet script")

    bookie = 'unibet'
    page = browser.new_page()
    config = MASTER_CONFIG[bookie]['sports']
    matches = []

    for sport, url in config.items():
        page.goto(url) 
        sleep(2)
        soup = BeautifulSoup(page.content(), 'html.parser')

        match_elements = soup.find_all('div', attrs={'data-test-name': "matchEvent"})
        
        # For each match in book, Deep Copy SCRAPING_TEMPLATE, fill it out and append to matches
        for match_element in match_elements:
            match = deepcopy(SCRAPING_TEMPLATE)
            match['bookie'] = 'unibet'
            match['url'] = url
            match['sport'] = sport
            date = match_element.find_previous('time').text
            if "Today" in date or "Tomorrow" in date:
                date = standardise_today_tomorrow_date(date, "day month year")
            time = match_element.find('div', attrs={'data-test-name': "clockDisplayContainer"})
            time = time.text if time else datetime.now().time().strftime("%H:%M") # Sport is live if not time
            if int(time[:2]) > 24:
                time = datetime.now().time().strftime("%H:%M") # Unibet make some games 60:00 or similar when game is live
            date_time = f'{date} {time}'
            # print(f'{match_element = }')
            match['date_time'] = round_to_nearest_five_minutes(datetime.strptime(date_time, "%d %B %Y %H:%M"))
            teams = match_element.find_all('div', attrs={'data-test-name': "eventParticipant"}) 
            match['team1'], match['team2'] = standardise_team_name(sport, teams[0].text), standardise_team_name(sport, teams[1].text)
            odds = match_element.find_all('div', attrs={'data-test-name': "outcomeBet"})
            odds = [odd.text for odd in odds if '+' not in odd.text and '-' not in odd.text]
            if odds and 'SUS' not in odds and '' not in odds:
                match['team1_odds'], match['team2_odds'] = float(odds[0]), float(odds[1])
                match = dacite.from_dict(data_class=BookieMatch, data=match)
                matches.append(match)

    print("Finished unibet script")
    return matches