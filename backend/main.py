# main.py
# Libraries
import os
import json
import importlib.util
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from utils import datetime_serializer


# Modules
from config import BOOKIES, SPORTS, BET_SIZE
from models import BookieMatch, MasterMatch


def run_bookie_script(module, browser):
    return module.main(browser)

def process_bookie_script(script_path):
    try:
        module_name = os.path.splitext(os.path.basename(script_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            if hasattr(module, 'main') and callable(getattr(module, 'main')):
                result = run_bookie_script(module, browser)
                browser.close()
                return result
            else:
                raise AttributeError(f"The module {module_name} does not have a callable 'main' function")
    except Exception as e:
        print(f"Error processing script {script_path}: {e}")
        raise

def bookie_matches_to_json(bookie_matches: list[BookieMatch]):
    bookie_matches = [asdict(match) for match in bookie_matches]
    with open('bookies.json', 'w') as f:
        json.dump(bookie_matches, f, default=datetime_serializer, indent=4)

def compile_bookie_matches_into_master_matches(bookie_matches: list[BookieMatch]) -> list[MasterMatch]:
    '''
    Takes in a list of bookie matches, compiles them all into master_matches.
    '''
    master_matches = []
    
    # Group bookie matches by the real match they represent
    grouped_bookie_matches = {}
    for bookie_match in bookie_matches:
        match_key = (bookie_match.date_time, bookie_match.sport, bookie_match.team1, bookie_match.team2)
        if match_key not in grouped_bookie_matches:
            grouped_bookie_matches[match_key] = []
        grouped_bookie_matches[match_key].append(bookie_match)

    # Loop through each group of bookie matches
    for match_key, group_bookie_match in grouped_bookie_matches.items():
        # Find the bookie matches with the highest odds for team1 and team2
        max_bookie_match1 = max(group_bookie_match, key=lambda x: x.team1_odds)
        max_bookie_match2 = max(group_bookie_match, key=lambda x: x.team2_odds)
        
        # Create a MasterMatch using the two highest odds bookie matches
        master_match = MasterMatch(bookie_match1=max_bookie_match1, bookie_match2=max_bookie_match2)
        
        # Add the created MasterMatch to the list of master matches
        master_matches.append(master_match)

    
    master_matches = sorted(master_matches, key=lambda x: x.coefficient)
    return master_matches

def master_matches_to_json(master_matches: list[MasterMatch]):
    master_matches_dicts = [asdict(match) for match in master_matches]
    with open('odds.json', 'w') as f:
        json.dump(master_matches_dicts, f, default=datetime_serializer, indent=4)

def main():
    '''
    Main - run in parallel
    '''
    bookies_dir = './bookies'
    bookie_matches: List[BookieMatch] = []
    master_matches: List[MasterMatch] = []

    # List all Python files in the bookies directory
    bookie_scripts = [
        os.path.join(bookies_dir, filename)
        for filename in os.listdir(bookies_dir)
        if filename.endswith('.py') and filename != '__init__.py'
    ]

    with ThreadPoolExecutor(max_workers=len(bookie_scripts)) as executor:
        future_to_script = {executor.submit(process_bookie_script, script): script for script in bookie_scripts}

        for future in as_completed(future_to_script):
            script = future_to_script[future]
            try:
                result = future.result()
                bookie_matches.extend(result)
            except Exception as exc:
                print(f'{script} generated an exception: {exc}')

    master_matches = compile_bookie_matches_into_master_matches(bookie_matches)
    master_matches_to_json(master_matches)

if __name__ == "__main__":
    main()