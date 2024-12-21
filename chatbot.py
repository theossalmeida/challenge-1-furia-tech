from flask import Flask, request
import requests
from backend_chatbot.LoL_Esports_API_Furia import get_lol_schedule
import json


# Parameters and variables for the API requisition https://esports-api.lolesports.com/
with open("keys_api.json", "r") as k: # More security for the API KEY not becoming public !! 
    keys_api = json.load(k)
k.close()

WPP_NUM_ID = keys_api['whatsapp_id_number']
WPP_TOKEN = keys_api['whats_app_api_token']
VERIFY_TOKEN = keys_api['verify_token']

app = Flask(__name__)

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if request.method == 'GET':
        # Verifies the token received
        if token == VERIFY_TOKEN:
            return challenge, 200  # Returns the challenge for validation
        return 'Token inválido!', 403

    if request.method == "POST":
        data = request.json  # Parse the JSON payload
        app.logger.debug(f"Incoming data: {data}")  # Log incoming data for debugging
        
        try:
            # Navigate to the relevant fields in the nested JSON structure
            entry = data['entry'][0]  # Extract the first entry
            change = entry['changes'][0]  # Extract the first change
            value = change['value']  # Get the value field

            # Extract contact and message details
            contact = value['contacts'][0]
            message = value['messages'][0]

            # Extract specific fields
            phone_number = contact['wa_id']
            text_body = message['text']['body']

            # Handle the message logic
            if text_body == "1":
                # Check if message matches the expected input
                next_games = get_lol_schedule()
                if next_games['status']:
                    send_message(phone_number, "Thank you for your message!")
                else:
                    send_message(phone_number, "Desculpe, não consegui obter os próximos jogos, tente novamente mais tarde")
            else:
                send_message(phone_number, "Por favor, escolha um número válido no menu.")
        except KeyError as e:
            app.logger.error(f"Missing key in incoming data: {e}")
            return "Bad Request: Missing key", 400
        except IndexError as e:
            app.logger.error(f"Unexpected list structure: {e}")
            return "Bad Request: Malformed data", 400

        return "OK", 200

def send_message(phone, message):
    url = f"https://graph.facebook.com/v21.0/{WPP_NUM_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    app.run(port=5000)