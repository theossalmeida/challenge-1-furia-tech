import requests
from datetime import datetime
import logging
from pathlib import Path
import pandas as pd
from itertools import chain


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
    filename= log_dir / "app_val.log",  # Files where log will be saved - remember to transfer the file to a database or log direct in it
    filemode="a" 
)

FURIA_ID = 2406

api_url = "https://vlr.orlandomm.net/api/v1/teams/{team_id}"
furia_info_url = api_url.format(team_id=FURIA_ID)

def get_val_roster() -> dict:

    try:
        roster_response = requests.get(furia_info_url)

        if not roster_response.ok:
            return {
                "status": False,
                "roster": ""
            }
        
        else:

            roster_data = roster_response.json()["data"]["players"]
            staff_data = roster_response.json()["data"]["staff"]

            # Function to get the player name like: FirstNmae "nick" LastName
            def get_nickname(row):
                real_name_list = row["name"].split(" ")
                real_firstname = real_name_list[0]
                real_lastname = real_name_list[1] if len(real_name_list) > 1 else ""
                if "tag" in row:
                    full_name = '[' +row["tag"].upper() + '] ' + real_firstname + ' "' + row["user"] + '" ' + real_lastname
                else:
                    full_name = '[PLAYER] ' + real_firstname + ' "' + row["user"] + '" ' + real_lastname
                return full_name
            
            # Creating players df
            roster_df = pd.DataFrame(roster_data)
            roster_df["fullname"] = roster_df.apply(get_nickname, axis=1)

            # Creating staff df
            staff_df = pd.DataFrame(staff_data)
            staff_df["fullname"] = staff_df.apply(get_nickname, axis=1)

            roster_list = list(chain(roster_df['fullname'].to_list(), staff_df['fullname'].to_list()))
            roster = '\n'.join(
                        roster_list
                     )

            return {
                'status': True,
                'roster': roster
            }
    
    except Exception as e:
        logging.error(f"Failed to get valorant roster: {e}")
        return {
            'status': False
        }


def get_val_schedule(past_or_next) -> dict:
    
    try:

        schedule_response = requests.get(furia_info_url)

        if not schedule_response.ok:
            return {
                "status": False,
                "games": ""
            }
        
        else:

            def get_match_info(row):

                    match_date = datetime.strftime(row['date'], '%d-%m-%y')
                    match_event = row['event']['name']
                    match_oponent = row['teams'][1]['name']

                    if 'points' in row['teams'][0].keys():
                        match_oponent_points = row['teams'][1]['points']
                        match_furia_points = row['teams'][0]['points']
                        match_full = f'{match_event} - {match_date} - FURIA {match_furia_points} x {match_oponent_points} {match_oponent}' 
                        return match_full
                    
                    match_full = f'{match_event} - {match_date} - FURIA x {match_oponent}' 
                    return match_full
            
            if past_or_next == 'next':

                response_json = schedule_response.json()["data"]["upcoming"]
                df = pd.DataFrame(response_json)
                df['date'] = pd.to_datetime(df['utc'])
                filtered_df = df.sort_values(by='date', ascending=False).head(5)
                filtered_df['match_info'] = filtered_df.apply(get_match_info, axis=1)

                games = 'Próximos jogos:\n' + "\n".join(
                    filtered_df['match_info'].to_list()
                ) + "\n\n/menu"

                return {
                    'status': True, 
                    'games': games
                }

            if past_or_next == "past":

                response_json = schedule_response.json()["data"]["results"]
                df = pd.DataFrame(response_json)
                df['date'] = pd.to_datetime(df['utc'])
                filtered_df = df.sort_values(by='date', ascending=False).head(5)
                
                filtered_df['match_info'] = filtered_df.apply(get_match_info, axis=1)

                games = "Últimos resultados:\n" + "\n".join(
                    filtered_df['match_info'].to_list()
                ) + "\n\n/menu"

                return {
                    'status': True,
                    'games': games
                }

    except Exception as e:
        logging.error(f'Failed to get valorant schedule for {past_or_next} games: {e}')
        return {
            'status': False
        }


if __name__ == "__main__":
    get_val_schedule('next')