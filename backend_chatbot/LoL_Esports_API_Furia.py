import requests
import pandas as pd
from datetime import datetime
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

def get_lol_schedule():
    
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
                    "team1name": events_series.apply(lambda x: x["match"]["teams"][0]["name"]),
                    "team1outcome": events_series.apply(lambda x: x["match"]["teams"][0]["result"]["outcome"]),
                    "team2name": events_series.apply(lambda x: x["match"]["teams"][1]["name"]),
                    "team2outcome": events_series.apply(lambda x: x["match"]["teams"][1]["result"]["outcome"]),
                    "leaguename": events_series.apply(lambda x: x["league"]["name"]),
                })
                league_schedule_filtered_df = league_schedule_df[(league_schedule_df['team1name'] == 'FURIA') | (league_schedule_df['team2name'] == 'FURIA')]
                league_schedule_filtered_df['furia_result'] = league_schedule_filtered_df.apply(lambda x: x['team1outcome'] if x['team1name'] == 'FURIA' else x['team2outcome'], axis=1)
            all_furia_schedule.append(league_schedule_filtered_df)

        # Gather all the df's of every league Furia is participating
        full_schedule_df = pd.concat(all_furia_schedule, ignore_index=True)
        full_schedule_df['date'] = pd.to_datetime(full_schedule_df["date"], format='%Y-%m-%dT%H:%M:%SZ')

        # Filter to obtain the next 5 games (considering the date of the call)
        current_date = datetime.now()
        furia_schedule = full_schedule_df[full_schedule_df['date'] > current_date].sort_values(by='date').head(5)
        
        # JSON to be returned with the information about next games (if it has)
        furia_next = {
            "status": True,
            "next_games": "No games" if furia_schedule.empty else furia_schedule.to_dict()
        }

        return furia_next

    else:
        print(league_response)
        return {"status": False}
    
# Test purpose only
if __name__ == "__main__":
    a = get_lol_schedule()
    print(a)