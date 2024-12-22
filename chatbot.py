from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import json
from backend_chatbot.get_lol_info import get_lol_schedule, get_lol_roster


BOT_USERNAME = "challenge_01_bot" # Replace with your bot's username


# Command to send the list of clickable commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Update here for the initial options the user should have
    message = (
        "Choose one of the commands below:\n\n"
        f"/league_of_legends\n"
        f"/valorant\n"
        f"/cs2\n"
        f"/r6\n"
        f"/rocket_league\n"
        f"/noticias\n"
        f"/help\n"
    )

    # Send the message
    await update.message.reply_text(message)
    return

# Show information options for the user
async def show_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Include the game on the command so our code knows what to look for
    game = update.message.text[1:]
    game_ = 'league' if game == 'league_of_legends' else game

    # Include here the options the user should have for each game
    message = (
        f"O que voce deseja saber sobre o nosso time de {game_}:\n\n"
        f"/proximos_jogos_{game_}\n"
        f"/ultimos_resultados_{game_}\n"
        f"/jogadores_{game_}\n"
        f"/help\n"
        f"/menu\n"
    )

    # Send the message
    await update.message.reply_text(message)
    return

# Next 5 games
async def show_next_games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Collect what game the user chose to receive information
    game = update.message.text.split("_")[2]

    # Message to let user know we are running the function
    await update.message.reply_text("Buscando próximos jogos...")
    
    if game == "league":

        schedule = get_lol_schedule("next_games")

        # Condition for cases where there are no next games on the function response
        if not schedule["status"]:
            await update.message.reply_text("Ocorreu um erro ao tentar buscar os próximos jogos, tente novamente mais tarde.\n\n/menu")

        else:
            games = schedule["games"]
            await update.message.reply_text(games + "\n\n/menu")

    else:
        await update.message.reply_text("Ainda nao tenho informacoes sobre essa modalidade, em breve poderei te ajudar!\n\n/menu")


# Next 5 games
async def show_roster(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Collect what game the user chose to receive information
    game = update.message.text.split("_")[1]

    # Message to let user know we are running the function
    await update.message.reply_text("Buscando nossa seleçåo...")
    
    if game == "league":

        roster = get_lol_roster()

        # Condition for cases where there are no next games on the function response
        if not roster["status"]:
            await update.message.reply_text("Ocorreu um erro ao tentar nossa seleçao, tente novamente mais tarde.\n\n/menu")

        else:
            team = roster["roster"]
            await update.message.reply_text("Esses sao nossos jogadores: \n" + team + "\n\n/menu")

    else:
        await update.message.reply_text("Ainda nao tenho informacoes sobre essa modalidade, em breve poderei te ajudar!\n\n/menu")


# Last 5 results
async def show_past_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Collect what game the user chose to receive information
    game = update.message.text.split("_")[2]
    
    # Message to let user know we are running the function
    await update.message.reply_text("Buscando últimos resultados...")

    if game == "league":
    
        schedule = get_lol_schedule("past_games")
    
        if not schedule["status"]:
            await update.message.reply_text("Ocorreu um erro ao tentar buscar os próximos jogos, tente novamente mais tarde.\n\n/menu")
    
        else:
            games = schedule["games"]
            await update.message.reply_text(f"Últimos resultados:\n{games}\n\n/menu")
    
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
    # Load the bot token securely
    with open("keys_api.json") as k:
        keys = json.load(k)
    bot_token = keys["telegram_token"]  # Ensure your JSON file contains your bot token

    # Create the Application
    application = Application.builder().token(bot_token).build()

    # Register basic handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", start))
    application.add_handler(CommandHandler("help", help))

    # Register handlers for each game options
    show_options_games = ['league_of_legends', 'valorant', 'cs2', 'r6', 'rocket_league']
    application.add_handler(CommandHandler(show_options_games, show_options))

    # Register handlers for each game next games
    commands_next_games = ["proximos_jogos_league", "proximos_jogos_valorant", "proximos_jogos_cs2", "proximos_jogos_r6", "proximos_jogos_rocket_league"]
    application.add_handler(CommandHandler(commands_next_games, show_next_games))

    # Register handlers for each game past results
    commands_last_results = ["ultimos_resultados_league", "ultimos_resultados_valorant", "ultimos_resultados_cs2", "ultimos_resultados_r6", "ultimos_resultados_rocket_league"]
    application.add_handler(CommandHandler(commands_last_results, show_past_results))

    # Register handlers for each game roster
    command_roster = ["jogadores_league", "jogadores_valorant", "jogadores_cs2", "jogadores_r6", "jogadores_rocket_league"]
    application.add_handler(CommandHandler(command_roster, show_roster))

    # Register handlers for each game news
    application.add_handler(CommandHandler("noticias", start))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
