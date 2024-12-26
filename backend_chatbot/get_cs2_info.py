from bs4 import BeautifulSoup
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

    # url to collect roster information 
    roster_url = hltv_url + "/team/8297/furia#tab-rosterBox"

    # Scrap to avoid cloudfare block
    scrapper = cloudscraper.create_scraper()
    response = scrapper.get(roster_url)

    # Check if response was successful 
    if not response.ok:
        schedule = {
            "status": False,
            "games": "" 
        }
        return schedule
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

            # Return the json containing status and the roster ready to be send for user
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

    try:

        # url to collect matches information
        roster_url = hltv_url + "/team/8297/furia#tab-matchesBox"

        # Test purpose only, change here if uria doesnt have any future games and you need to test
        # roster_url = hltv_url + "/team/12374/verdant#tab-matchesBox"

        # Scrap to avoid cloudfire block
        scrapper = cloudscraper.create_scraper()
        response = scrapper.get(roster_url)

        # Check if response was successful
        if not response.ok:
            schedule = {
                "status": False,
                "games": "" 
            }
        
        else:

            soup = BeautifulSoup(response.text, 'html.parser')
            matches_div = soup.find('div', id='matchesBox')
            has_matches = matches_div.find('div', class_='empty-state')

            # Check if user want next games or previous results
            if past_or_next == "next":
                if not has_matches:
                    
                    # collect first table with upcoming matches
                    next_matches_table = matches_div.find_all('table', class_='table-container match-table')[0]
                    next_matches_event = next_matches_table.find_all('tr', class_='event-header-cell')[0].find('a').text.strip().split(' -')[0]
                    next_dates, next_matches = [], [] 
                    for i, row in enumerate(next_matches_table.find_all('tr', class_='team-row')):
                        
                        # only collect max 5 next matches
                        if i >= 5:
                            break

                        date_match = row.find('td', class_='date-cell').find('span').text.strip()
                        date_fix = datetime.now().strftime("%d/%m/%Y") if ":" in date_match else date_match
                        next_dates.append(date_fix)

                        has_oponent = row.find_all('div')[2].find('a', class_='team-name team-2')
                        oponent = has_oponent.text.strip() if has_oponent else "TBD"
                        game_ = f"FURIA x {oponent}"
                        next_matches.append(game_)
                    
                        games = "\n".join(
                            [f"{next_matches_event} - {date} - {game}" for date, game in zip(next_dates, next_matches)]
                        )

                        furia_next = {
                            "status": True,
                            "games": f"Próximos jogos: \n{games}\n\n/menu"
                        }

                        return furia_next

                else:
                    games = "Ainda nao temos a data dos proximos jogos da Furia, mas fique ligado, assim que tivermos vamos te informar!\n\n/menu"
                    
                # JSON to be returned with the information about next games (if it has)
                furia_next = {
                    "status": True,
                    "games": games
                }

                return furia_next

            else:

                past_dates, past_matches = [], []
                last_matches_table = matches_div.find_all('table', class_='table-container match-table')[0 if has_matches else 1]
                last_matches_event = last_matches_table.find_all('tr', class_='event-header-cell')[0].find('a').text.strip().split(' -')[0]

                for i, row in enumerate(last_matches_table.find_all('tr', class_='team-row')):
                    
                    # only collect max 5 matches results
                    if i >= 5:
                        break

                    date_match = row.find('td', class_='date-cell').find('span').text.strip()
                    past_dates.append(date_match)

                    results_cells = row.find('td', class_='team-center-cell').find('div', class_='score-cell').find_all('span')
                    furia_score = results_cells[0].text.strip()
                    oponent_score = results_cells[2].text.strip()
                    oponent = row.find_all('div')[2].find('a', class_='team-name team-2').text.strip()
                    result_match = f"FURIA {furia_score} x {oponent_score} {oponent}"
                    past_matches.append(result_match)
                
                games = "\n".join(
                    [f"{last_matches_event} - {date} - {result}" for date, result in zip(past_dates, past_matches)]
                )

                furia_past = {
                    "status": True,
                    "games": f"Últimos resultados: \n{games}\n\n/menu"
                }

                return furia_past

    except Exception as e:
        logging.error(f"Error ocurred while fetching data for cs2 schedule {past_or_next} games: {e}")                  


# Test purpose only
if __name__ == '__main__':
    a = get_cs2_schedule("past")
    print(a)