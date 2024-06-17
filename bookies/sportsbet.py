# sportsbet.py
import dacite
from models import BookieMatch, MasterMatch, SCRAPING_TEMPLATE
from copy import deepcopy
from bs4 import BeautifulSoup

def main() -> list[BookieMatch]:
    print("Running sportsbet script")

    sports = []
    matches = []
    base_url = 'www.sportsbet.com'

    for sport in sports:
        page = '' # Some selenium/playwright logic here
        soup = BeautifulSoup(page.content(), 'html.parser')
        match_elements = soup.find_all('div')
        
        # For each match in book, Deep Copy SCRAPING_SCHEMA, fill it out and append to matches
        for match_element in match_elements:
            match = deepcopy(SCRAPING_TEMPLATE)
            match = dacite.from_dict(data_class=BookieMatch, data=match)
            matches.append(match)

    return matches


if __name__ == "__main__":
    main()
