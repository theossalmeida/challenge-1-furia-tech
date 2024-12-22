import requests
import pandas as pd
from datetime import datetime, date
import json


# Parameters and variables for the API requisition https://esports-api.lolesports.com/
with open("keys_api.json", "r") as k: # More security for the API KEY not becoming public !! 
    keys_api = json.load(k)
k.close()

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
        if past_or_next == "next_games":

            # Filter to obtain the next 5 games (considering the date of the call)
            furia_schedule = full_schedule_df[full_schedule_df['date'] > current_date].sort_values(by='date').head(5)

            if not furia_schedule.empty:
                games = "\n".join(
                    f"{game['league']} - {game['date']} - {game['furia']} x {game['oponente']}" for i, game in furia_schedule.iterrows()
                    )
            else:
                games = "Ainda nao temos a data dos proximos jogos da Furia, mas fique ligado, assim que tivermos vamos te informar!"
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
                "games": games
            }

        return furia_next

    else:
        print(league_response)
        return {"status": False}
    
# Test purpose only
if __name__ == "__main__":
    a = get_lol_schedule()
    print(a)