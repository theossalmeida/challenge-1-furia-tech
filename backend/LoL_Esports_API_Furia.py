# Script contendo a API que nos retornará os dados sobre o time profissional masculino da Furia no League of Legends (antigo CBLOL)

import requests
import pandas as pd
from flask import Flask


api_lol = Flask(__name__)

with open("key.txt", "r+") as key:
    api_key = key
key.close()

def get_response_dict(url: str) -> dict:
    headers = {"x-api-key": r"0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
    response = requests.get(url, headers)
    print(response.json())
    if str(response.status_code)[0] != 2: #Verifica se a resposta da API foi sucesso (começando com 2) ou não)
        return {"error": True}
    
    else:
        return {
            "error": False,
            "status_code": response.status_code,
            "json": response.json()
        }

league_response = get_response_dict("https://esports-api.lolesports.com/persisted/gw/getLeagues")
league_id = league_response["json"]["data"]["league"] if league_response["error"] == False else 0

@api_lol.route("/lol_schedule")
def get_lol_schedule():
    url_schedule = "https://esports-api.lolesports.com/persisted/gw/getLeagues" # API não-oficial: https://vickz84259.github.io/lolesports-api-docs/#operation
    response = requests.get(url_schedule)