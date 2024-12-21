from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json


# Define a command function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Olá, bem vindo ao seu assistente furioso! O que você deseja saber hoje ?')

# Define a message handler
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

# Main function
def main():

    # Remember to secure your token somewhere safe, do not share it on the code (ideally you can use GCP or other cloud storage more safe)
    with open("keys_api.json") as k:
        keys = json.load(k)
    bot_token = keys["telegram_token"]  # Ensure your JSON file has your telegram key or change the way you read your token

    # Create the Application
    application = Application.builder().token(bot_token).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
