# Script contendo a API que nos retornará os dados sobre o time profissional masculino da Furia no League of Legends (antigo CBLOL)

import requests
import pandas as pd
from flask import Flask


api_lol = Flask(__name__)

@api_lol.route("/lol_schedule")
def get_lol_schedule():
    pass