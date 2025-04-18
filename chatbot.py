from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from load_dotenv import load_dotenv
import os
import logging
from backend_chatbot import (
    get_cs2_info as cs2,
    get_lol_info as lol,
    get_valorant_info as val,
    )


"""
Due to the fact that a chatbot can be accessd by thousands of people simultaneosly, and this is only for a challenge / practice, 
the logging cofinguration will be just for the errors inside the functions, there will be no log for the start/on going of every step
but for a production environment is really important to have it all logged and stored in a database, this will make it much easier
to fix errors and find bugs.
"""

# Basic configuration
logging.basicConfig(
    level=logging.DEBUG,  
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log message format
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="app_chatbot.log",  # Files where log will be saved - remember to transfer the file to a database or log direct in it
    filemode="a" 
)

BOT_USERNAME = "challenge_01_bot" # Replace with your bot's username

# Dict with all the functions used in the async functions 
# (this avoid a lot of if-else statements and make the code more clean)
games_functions = {
            "jogos_league": lol.get_lol_schedule,
            "jogadores_league": lol.get_lol_roster,
            "jogos_cs2": cs2.get_cs2_schedule,
            "jogadores_cs2": cs2.get_cs2_roster,
            "jogos_valorant": val.get_val_schedule,
            "jogadores_valorant": val.get_val_roster,
        }

# Command to send the list of clickable commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Update here for the initial options the user should have
        message = (
            "Sobre qual jogo voce deseja ter informaçoes ?\n\n"
            f"/league_of_legends\n"
            f"/valorant\n"
            f"/cs2\n"
            f"/noticias\n"
            f"/help\n"
        )

        # Send the message
        await update.message.reply_text(message)
        return
    except Exception as e:
        logging.error(f"Error has occured to start bot for user: {e}")


# Show information options for the user
async def show_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    try:
        # Include the game on the command so our code knows what to look for
        game = update.message.text[1:]
        game_ = 'league' if game == 'league_of_legends' else game

        # Include here the options the user should have for each game
        message = (
            f"O que voce deseja saber sobre o nosso time de {game_}:\n\n"
            f"/proximos_jogos_{game_}\n"
            f"/ultimos_jogos_{game_}\n"
            f"/jogadores_{game_}\n"
            f"/help\n"
            f"/menu\n"
        )

        # Send the message
        await update.message.reply_text(message)
        return
    except Exception as e:
        logging.error(f"Error has occured while showing user the game option: {e}")


# Next 5 games
async def show_next_games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    try:
        # Collect what game the user chose to receive information
        next_function = update.message.text.split("_")[1] + "_" + update.message.text.split("_")[2]

        # Check if the game selected already has the correct function to collect data
        if next_function in games_functions.keys():
   
            # Message to let user know we are running the function
            await update.message.reply_text("Buscando próximos jogos...")

            # Call the correct function for each game (the 'next' arg make sure we collect the next games, not the previous results)
            schedule = games_functions[next_function]('next')
            
            # Check if the function successfully collected data
            if not schedule["status"]:
                await update.message.reply_text("Ocorreu um erro ao tentar buscar os próximos jogos, tente novamente mais tarde.\n\n/menu")
        
            else:
                games = schedule["games"]
                await update.message.reply_text(games)
            
        else:
            await update.message.reply_text("Ainda nao tenho informacoes sobre essa modalidade, em breve poderei te ajudar!\n\n/menu")
    
    except Exception as e:
        logging.error(f"Error has occured while fetching next games for user: {e}")


# Next 5 games
async def show_roster(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Collect what game the user chose to receive information
    command = update.message.text[1:]

    if command in games_functions.keys():

        roster = games_functions[update.message.text[1:]]()

        # Message to let user know we are running the function
        await update.message.reply_text("Buscando nossa seleçåo...")

        # Condition for cases where there are no next games on the function response
        if not roster["status"]:
            await update.message.reply_text("Ocorreu um erro ao tentar nossa seleçao, tente novamente mais tarde.\n\n/menu")
            return

        else:
            team = roster["roster"]
            await update.message.reply_text("Esses sao nossos jogadores:\n\n" + team + "\n\n/menu")
            return

    await update.message.reply_text("Ainda nao tenho informacoes sobre essa modalidade, em breve poderei te ajudar!\n\n/menu")


# Last 5 results
async def show_past_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Collect what game the user chose to receive information
    past_function = update.message.text.split("_")[1] + "_" + update.message.text.split("_")[2] 

    if past_function in games_functions:

        # Message to let user know we are running the function
        await update.message.reply_text("Buscando últimos resultados...")

        schedule = games_functions[past_function]('past')
        
        if not schedule["status"]:
            await update.message.reply_text("Ocorreu um erro ao tentar buscar os últimos resultados, tente novamente mais tarde.\n\n/menu")
    
        else:
            games = schedule["games"]
            await update.message.reply_text(games)
        
    else:
        await update.message.reply_text("Ainda nao tenho informacoes sobre essa modalidade, em breve poderei te ajudar!\n\n/menu")


# Help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Eu só consigo te ajudar com as informações sobre os nossos times e as notícias.\n"
        "Caso precise de ajuda sobre algum de nossos serviços ou produtos, entre em contato pelos nossos canais de atendimento:\n"
        "--link1--\n--link2--\n\n"
        f"/menu"
    )
    await update.message.reply_text(message)


# Main function
def main():
    load_dotenv()

    bot_token = os.getenv('BOT_TOKEN') # Load the bot token securely

    # Create the Application
    application = Application.builder().token(bot_token).build()

    # Register basic handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("noticias", start))
    
    # Register handlers for each game options
    show_options_games = ['league_of_legends', 'valorant', 'cs2', 'r6', 'rocketleague']
    application.add_handler(CommandHandler(show_options_games, show_options))

    # Register handlers for each game next games
    commands_next_games = ["proximos_jogos_league", "proximos_jogos_valorant", "proximos_jogos_cs2", "proximos_jogos_r6", "proximos_jogos_rocketleague"]
    application.add_handler(CommandHandler(commands_next_games, show_next_games))

    # Register handlers for each game past results
    commands_last_results = ["ultimos_jogos_league", "ultimos_jogos_valorant", "ultimos_jogos_cs2", "ultimos_jogos_r6", "ultimos_jogos_rocketleague"]
    application.add_handler(CommandHandler(commands_last_results, show_past_results))

    # Register handlers for each game roster
    command_roster = ["jogadores_league", "jogadores_valorant", "jogadores_cs2", "jogadores_r6", "jogadores_rocketleague"]
    application.add_handler(CommandHandler(command_roster, show_roster))


    # Run the bot
    application.run_polling()


if __name__ == '__main__':
    main()
