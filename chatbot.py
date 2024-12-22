from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import json
from backend_chatbot.LoL_Esports_API_Furia import get_lol_schedule

BOT_USERNAME = "challenge_01_bot"  # Replace with your bot's username

# Command to send the list of clickable commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("League of Legends", callback_data="league_of_legends")],
        [InlineKeyboardButton("Valorant", callback_data="valorant")],
        [InlineKeyboardButton("CS2", callback_data="cs2")],
        [InlineKeyboardButton("Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Escolha um dos comandos abaixo:", reply_markup=reply_markup)

# Callback handler for all buttons
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "league_of_legends":
        await query.message.reply_text("Você escolheu League of Legends!")
        await show_lol_options(update, context)
    elif query.data == "valorant":
        await query.message.reply_text("Você escolheu Valorant!")
        await show_valorant_options(update, context)
    elif query.data == "cs2":
        await query.message.reply_text("Você escolheu CS2!")
        await show_cs2_options(update, context)
    elif query.data == "help":
        await query.message.reply_text("Menu de ajuda solicitado!")
        await help(update, context)
    elif query.data == "proximos_jogos_lol":
        await query.message.reply_text("Buscando os próximos jogos...")
        await show_next_games_lol(update, context)
    elif query.data == "ultimos_resultados_lol":
        await query.message.reply_text("Buscando os últimos resultados...")
        await show_past_results_lol(update, context)
    elif query.data == "voltar":
        await start(update.callback_query, context)

# League of Legends options
async def show_lol_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Próximos Jogos", callback_data="proximos_jogos_lol")],
        [InlineKeyboardButton("Últimos Resultados", callback_data="ultimos_resultados_lol")],
        [InlineKeyboardButton("Voltar", callback_data="voltar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("Escolha uma das opções abaixo:", reply_markup=reply_markup)

# Valorant options
async def show_valorant_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Próximos Jogos", callback_data="proximos_jogos_val")],
        [InlineKeyboardButton("Últimos Resultados", callback_data="ultimos_resultados_val")],
        [InlineKeyboardButton("Voltar", callback_data="voltar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("Escolha uma das opções abaixo:", reply_markup=reply_markup)

# CS2 options
async def show_cs2_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Próximos Jogos", callback_data="proximos_jogos_cs2")],
        [InlineKeyboardButton("Últimos Resultados", callback_data="ultimos_resultados_cs2")],
        [InlineKeyboardButton("Voltar", callback_data="voltar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("Escolha uma das opções abaixo:", reply_markup=reply_markup)

# Próximos jogos para LoL
async def show_next_games_lol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    schedule = get_lol_schedule("next_games")

    # Condition for cases where there are no next games on the function response
    if not schedule["status"]:
        await update.callback_query.message.reply_text("Ocorreu um erro ao tentar buscar os próximos jogos, tente novamente mais tarde")

    else:
        games = schedule["games"]
        await update.callback_query.message.reply_text(f"Próximos jogos:\n{games}")

# Últimos resultados para LoL
async def show_past_results_lol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    schedule = get_lol_schedule("past_games")
    if not schedule["status"]:
        await update.callback_query.message.reply_text("Ocorreu um erro ao tentar buscar os próximos jogos, tente novamente mais tarde")
    else:
        games = schedule["games"]
        await update.callback_query.message.reply_text(f"Últimos resultados:\n{games}")

# Help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Eu só consigo te ajudar com as informações sobre os nossos times e as notícias.\n"
        "Caso precise de ajuda sobre algum de nossos serviços ou produtos, entre em contato pelos nossos canais de atendimento:\n"
        "--link1--\n--link2--"
    )
    await update.callback_query.message.reply_text(message)

# Main function
def main():
    # Load the bot token securely
    with open("keys_api.json") as k:
        keys = json.load(k)
    bot_token = keys["telegram_token"]  # Ensure your JSON file contains your bot token

    # Create the Application
    application = Application.builder().token(bot_token).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
