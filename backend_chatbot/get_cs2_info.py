from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import cloudscraper
import logging
from pathlib import Path


"""
Due to the fact that a chatbot can be accessd by thousands of people simultaneosly, and this is only for a challenge / practice, 
the logging cofinguration will be just for the errors inside the functions, there will be no log for the start/on going of every step
but for a production environment is really important to have it all logged and stored in a database, this will make it much easier
to fix errors and find bugs.
"""

# Write here the path where the logs will be saved
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True) # creates the folder if it doesn't exist

# Basic configuration
logging.basicConfig(
    level=logging.DEBUG,  
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
    datefmt="%Y-%m-%d %H:%M:%S",
    filename= log_dir / "app_cs2.log",  # Files where log will be saved - remember to transfer the file to a database or log direct in it
    filemode="a" 
)

hltv_url = "https://www.hltv.org"

def get_cs2_roster() -> dict:

    roster_url = hltv_url + "/team/8297/furia#tab-rosterBox"

    scrapper = cloudscraper.create_scraper()
    response = scrapper.get(roster_url)
    if not response.ok:
        schedule = {
            "status": False,
            "games": f"Nao foi possivel obter os jogadores no momento, tente novamente mais tarde!" 
        }
    else:
        try:
            # Collecting roster info
            soup = BeautifulSoup(response.text, 'html.parser')
            players_nick_raw = soup.find_all('div', class_='playersBox-playernick')
            players_nick = [p.text.strip() for p in players_nick_raw]

            # Collecting individual player info
            players_link_td = soup.find_all('td', class_='playersBox-first-cell')
            players_link = [td.find('a')['href'] for td in players_link_td if td.find('a')]
            players_real_name = []
            # Going through every player to collect their real names
            for i, link in enumerate(players_link):
                player_scrapper = scrapper.get(hltv_url + link)
                soup_player = BeautifulSoup(player_scrapper.text, 'html.parser')
                div_name = soup_player.find('div', class_='playerRealname')
                first_name = div_name.text.strip().split(' ')[0]
                last_name = div_name.text.strip().split(' ')[1]
                players_real_name.append(first_name + ' "' + players_nick[i] + '" ' + last_name)

            # Preparing the string to be send for the user
            roster = "\n".join([
                ('[COACH] ' if i == 0 else '[PLAYER] ') + p for i, p in enumerate(players_real_name)
            ])

            return {
                "status": True,
                "roster": roster 
            }
        except Exception as e:
            logging.error(f"Error occured while getting cs2 roster: {e}")
            return {
                "status": False,
                "games": ""
            }
            

def get_cs2_schedule(past_or_next) -> dict:
    pass


# Test purpose only
if __name__ == '__main__':
    a = get_cs2_roster()
    print(a)