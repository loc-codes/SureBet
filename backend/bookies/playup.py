import dacite
from models import BookieMatch, SCRAPING_TEMPLATE
from config import MASTER_CONFIG
from copy import deepcopy
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import dateparser
from utils import standardise_team_name, round_to_nearest_five_minutes, standardise_today_tomorrow_date
import re

def main(browser) -> list[BookieMatch]:
    print("Running playup script")

    bookie = 'playup'
    page = browser.new_page()
    config = MASTER_CONFIG[bookie]['sports']
    matches = []

    for sport, url in config.items():
        page.goto(url) # Some selenium/playwright logic here
        soup = BeautifulSoup(page.content(), 'html.parser')

        match_elements = soup.find_all('a', attrs={'class': "sc-kSsbVf jrKgUV"})
        
        # For each match in book, Deep Copy SCRAPING_TEMPLATE, fill it out and append to matches
        for match_element in match_elements:
            match = deepcopy(SCRAPING_TEMPLATE)
            match['bookie'] = 'playup'
            match['url'] = url
            match['sport'] = sport
            date = match_element.find_previous('div', attrs={'class': "sc-dYOqWG hzschq"}).text.strip()
            time = match_element.find('div', attrs={'class': "sc-kDrquE eVpedz flex items-center"}).text.strip()
            if "Live" in time:
                time = datetime.now().time().strftime("%H:%M")
            else:
                time = re.search(r"(\d{1,2}:\d{2})", time).group(1)
            if "Today" in date or "Tomorrow" in date:
                date = standardise_today_tomorrow_date(date)
            date_time = f'{date} {time}'
            try:
                match['date_time'] = round_to_nearest_five_minutes(datetime.strptime(date_time, "%A %d %b %Y %H:%M"))
            except:
                match['date_time'] = round_to_nearest_five_minutes(datetime.strptime(date_time, "%d %b %Y %H:%M"))
            teams = match_element.find_all('div', attrs={'class': "col-start-1 font-semibold text-left"}) 
            match['team1'], match['team2'] = standardise_team_name(sport, teams[0].text), standardise_team_name(sport, teams[1].text)
            odds_rows = match_element.find_all('div', attrs={'class': "col-span-3 flex flex-row items-stretch"})
            odds = [odds_row.find('div', attrs={'class': "flex-1 flex items-stretch m-1"}).text for odds_row in odds_rows]
            if 'SUS' not in odds:
                match['team1_odds'], match['team2_odds'] = float(odds[0]), float(odds[1])
                match = dacite.from_dict(data_class=BookieMatch, data=match)
                matches.append(match)

    print("Finished playup script")
    return matches