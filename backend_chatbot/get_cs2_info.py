from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import cloudscraper


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


# Test purpose only
if __name__ == '__main__':
    a = get_cs2_roster()
    print(a)