import requests
from datetime import datetime
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

def get_r6_roster() -> dict:
    pass


def get_r6_schedule(past_or_next) -> dict:
    pass