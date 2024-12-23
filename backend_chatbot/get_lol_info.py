import requests
import pandas as pd
from datetime import datetime, date
import json
from bs4 import BeautifulSoup
import os
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

# Parameters and variables for the API requisition https://esports-api.lolesports.com/
keys_path = os.path.join("../..", "keys_api.json")
keys_path = "/Users/theo/chall-01-furia/challenge-1-furia-tech/keys_api.json"
with open(keys_path, "r") as k: # More security for the API KEY not becoming public !! 
    keys_api = json.load(k)

key = keys_api['lol_esports_api_key']

header = {"x-api-key": key, "Content-Type": "application/json"}
query_params = {
    "hl": "en-US",  # Change here for the preferred language
}

def get_lol_schedule(past_or_next) -> dict:
    
    url_schedule = "https://esports-api.lolesports.com/persisted/gw/getSchedule"
    url_leagues = "https://esports-api.lolesports.com/persisted/gw/getLeagues"
    league_response = requests.get(url_leagues, headers=header, params=query_params)
    
    all_furia_schedule = []

    if league_response.ok:
        try:
            leagues = league_response.json()['data']['leagues']

            # Collecting all IDs leagues Furia is participating
            leagues_df = pd.DataFrame(leagues)
            furia_participating_leagues = ["CBLOL", "LTA"] # Remember to include all leagues Furia is participating (may connect to database of competitions to make it automatic)

            # Collecting the IDs of the leagues
            furia_leagues = leagues_df[leagues_df["name"].isin(furia_participating_leagues)]
            furia_participating_leagues_ids = furia_leagues["id"].to_list()

            for id in furia_participating_leagues_ids:
                # Include the ID in the parameters for the schedule request
                query_params["leagueId"] = id
                league_schedule_response = requests.get(url_schedule, headers=header, params=query_params)

                # Check if the request was successfull
                if not league_schedule_response.ok:

                    # If failed, return false
                    {
                        "status": False,
                        "next_games": "failed to get next games"
                    }

                else:

                    # Extract events as a Series
                    events = league_schedule_response.json()["data"]["schedule"]["events"]
                    events_series = pd.Series(events)

                    # Extract relevant fields directly using Series methods
                    league_schedule_df = pd.DataFrame({
                        "date": events_series.apply(lambda x: x["startTime"]),
                        "league": events_series.apply(lambda x: x["league"]["name"]),
                        "team1name": events_series.apply(lambda x: x["match"]["teams"][0]["name"]),
                        "team1outcome": events_series.apply(lambda x: x["match"]["teams"][0]["result"]["outcome"]),
                        "team1maps": events_series.apply(lambda x: x["match"]["teams"][0]["result"]["gameWins"]),
                        "team2name": events_series.apply(lambda x: x["match"]["teams"][1]["name"]),
                        "team2outcome": events_series.apply(lambda x: x["match"]["teams"][1]["result"]["outcome"]),
                        "team2maps": events_series.apply(lambda x: x["match"]["teams"][1]["result"]["gameWins"]),
                        "leaguename": events_series.apply(lambda x: x["league"]["name"]),
                    })
                    league_schedule_filtered_df = league_schedule_df[(league_schedule_df['team1name'] == 'FURIA') | (league_schedule_df['team2name'] == 'FURIA')]
                all_furia_schedule.append(league_schedule_filtered_df)

            # Gather all the df's of every league Furia is participating
            full_schedule_df = pd.concat(all_furia_schedule, ignore_index=True)
            full_schedule_df['date'] = pd.to_datetime(full_schedule_df["date"], format='%Y-%m-%dT%H:%M:%SZ')

            # Organizing the columns we will use in the message
            full_schedule_df["furia"] = full_schedule_df.apply(lambda x: x["team1name"] if x["team1name"] == "FURIA" else x["team2name"], axis=1)
            full_schedule_df["resultado_furia"] = full_schedule_df.apply(lambda x: x["team1outcome"] if x["team1name"] == "FURIA" else x["team2outcome"], axis=1)
            full_schedule_df["games_furia"] = full_schedule_df.apply(lambda x: x["team1maps"] if x["team1name"] == "FURIA" else x["team2maps"], axis=1)
            full_schedule_df["oponente"] = full_schedule_df.apply(lambda x: x["team2name"] if x["team1name"] == "FURIA" else x["team1name"], axis=1)
            full_schedule_df["games_oponente"] = full_schedule_df.apply(lambda x: x["team2maps"] if x["team1name"] == "FURIA" else x["team1maps"], axis=1)
            

            current_date = datetime.now()
            # Condition to filter correctly if user asked for the next 5 games or the last 5
            if past_or_next == "next":

                # Filter to obtain the next 5 games (considering the date of the call)
                furia_schedule = full_schedule_df[full_schedule_df['date'] > current_date].sort_values(by='date').head(5)

                if not furia_schedule.empty:
                    schedule_formatted = "\n".join(
                        f"{game['league']} - {game['date']} - {game['furia']} x {game['oponente']}" for i, game in furia_schedule.iterrows()
                        )
                    
                    f"Prximos jogos:\n{schedule_formatted}\n\n/menu"

                else:
                    games = "Ainda nao temos a data dos proximos jogos da Furia, mas fique ligado, assim que tivermos vamos te informar!\n\n/menu"
                
                # JSON to be returned with the information about next games (if it has)
                furia_next = {
                    "status": True,
                    "games": games
                }

            else:
                # Filter to obtain the last 5 games (considering the date of the call)
                furia_schedule = full_schedule_df[full_schedule_df['date'] <= current_date].sort_values(by='date', ascending=False).head(5)

                # Deep copy df to make all changes necessaires
                df_to_send = furia_schedule.copy(deep=True)

                # Create columns to final dict
                df_to_send["resultado_game"] = df_to_send.apply(lambda x: f"{x['furia']} {x['games_furia']} x {x['games_oponente']} {x['oponente']}", axis=1)
                df_to_send["outcome"] = df_to_send.apply(lambda x: "Derrota" if x['resultado_furia'] == 'loss' else 'Vitória', axis=1)
                df_to_send["date"] = df_to_send["date"].dt.strftime('%d-%m-%Y')

                # Keep only the necessaire columns
                columns_to_keep = ["date", "league", "resultado_game", "outcome"]
                df_to_send = df_to_send[columns_to_keep]
                games = "\n".join(
                        f"{game['league']} - {game['date']} - {game['outcome']} - {game['resultado_game']}" for i, game in df_to_send.iterrows()
                        )
                    

                # JSON to be returned with the information about next games (if it has)
                furia_next = {
                    "status": True,
                    "games": f"Últimos resultados:\n{games}\n\n/menu"
                }

            return furia_next
        
        except Exception as e:
            # Here you should threat  every exception case to be more specific on the logging, and also treat the error correctly
            logging.error(f"Error occured while getting league of legends schedule for {past_or_next} games: {e}")
            return {
                "status": False,
                "games": "Error occured while getting games."
            }
    else:
        print(league_response)
        return {"status": False}


def get_lol_roster():

    # API url to collect teams data
    url_teams = "https://esports-api.lolesports.com/persisted/gw/getTeams"
    league_response = requests.get(url_teams, headers=header, params=query_params)

    # Check if request was successful
    if not league_response.ok:
        return {"status":False}
    
    else:
        try:
            # Create DF to treat data
            all_teams_df = pd.DataFrame(league_response.json()["data"]["teams"])

            # Filter only FURIA data
            filtered_df = all_teams_df[all_teams_df["name"] == "FURIA"]
            for i, row in filtered_df.iterrows():
                # Convert the players json into a df
                furia_df = pd.DataFrame(row["players"])
                break
            
            # Create column to correctly display player name
            furia_df["player_name"] = furia_df.apply(lambda x: f'{x["firstName"]} "{x["summonerName"]}" {x["lastName"]}', axis=1)
            furia_df["role"] = furia_df.apply(lambda x: "adc" if x["role"] == "bottom" else x["role"], axis=1)
            roles_index = {
                "top": 1,
                "jungle": 2,
                "mid": 3,
                "adc": 4,
                "support": 5
            }
            furia_df["role_idx"] = furia_df.apply(lambda x: roles_index[x["role"]], axis=1)

            furia_df = furia_df.sort_values(by="role_idx", ascending=True)

            # Prepare the string to be send to the final user
            roster = "\n".join(
                f'{x["role"]} - {x["player_name"]}' for i, x in furia_df.iterrows()
            )

            return {"status": True,
                    "roster": roster}
        except Exception as e:
            logging.error(f"Error occured while getting roster for league of legends: {e}")


# Test purpose only
if __name__ == "__main__":
    a = get_lol_roster()
