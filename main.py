# main.py
# Libraries
from bs4 import BeautifulSoup
import os
import importlib.util


# Modules
from config import BOOKIES, SPORTS, BET_SIZE, BOOKIES_SPORTS_CONFIG
from models import BookieMatch, MasterMatch

# Directory containing the bookie scripts
bookies_dir = './bookies'
bookie_matches: list[BookieMatch] = []
master_matches: list[MasterMatch] = []

def run_bookie_script(script_path: str) -> list[BookieMatch]:
    """
    Dynamically loads and executes a Python script given its file path.

    This function takes the path to a Python script, loads it as a module,
    and executes its main function if it exists. The module is loaded
    using importlib utilities to ensure it can be handled dynamically.

    Parameters:
    script_path (str): The file path to the Python script to be executed.

    Example usage:
    run_bookie_script('./bookies/sportsbet.py')

    Notes:
    - The script must contain a function named 'main' to be executed.
    - If the 'main' function does not exist in the script, a message is printed.
    """
    module_name = os.path.splitext(os.path.basename(script_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, 'main'):
        return module.main()
    else:
        print(f"No main function found in {module_name}")
        return []

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

    return master_matches

def main():
    '''
    Main - currently sequential, eventually run in parallel
    '''
    # List all Python files in the bookies directory
    for filename in os.listdir(bookies_dir):
        if filename.endswith('.py'):
            script_path = os.path.join(bookies_dir, filename)
            bookie_matches = bookie_matches + run_bookie_script(script_path)
            

if __name__ == "__main__":
    main()