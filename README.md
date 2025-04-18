# Esports Chatbot

This repository contains a Telegram chatbot designed to provide information about the esports team FURIA, including schedules, rosters, and past results for games like Counter-Strike 2 (CS2), League of Legends (LoL), and Valorant. The bot is built using Python and leverages APIs and web scraping to fetch real-time data.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Features
- Displays upcoming match schedules for FURIA in CS2, LoL, and Valorant.
- Provides past match results for the supported games.
- Lists current team rosters, including players and staff.
- Interactive command-based interface via Telegram.
- Error logging for debugging (logs saved to a `logs` directory).
- Supports multiple esports titles with a modular backend.

## Technologies Used
- **Python 3.8+**: Core programming language.
- **python-telegram-bot**: For Telegram bot integration.
- **BeautifulSoup & cloudscraper**: For web scraping CS2 data from HLTV.org.
- **pandas**: For data manipulation and processing.
- **requests**: For making API calls to fetch LoL and Valorant data.
- **logging**: For error tracking and debugging.
- **dotenv**: For secure environment variable management.
- **APIs**:
  - LoL Esports API (for LoL schedules and rosters).
  - VLR API (for Valorant schedules and rosters).

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/esports-chatbot.git
   cd esports-chatbot
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.8+ installed. Then, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory and add the following:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   API_KEY=your_lol_esports_api_key
   ```
   - Obtain a Telegram bot token from [BotFather](https://t.me/BotFather).
   - Get the LoL Esports API key from the [LoL Esports API portal](https://developer.riotgames.com/).

4. **Run the Bot**:
   Start the bot by running:
   ```bash
   python chatbot.py
   ```

5. **Interact with the Bot**:
   Open Telegram, search for your bot (e.g., `@challenge_01_bot`), and use the `/start` command to begin.

## Usage
The bot responds to the following commands:
- `/start` or `/menu`: Displays the main menu with game options (CS2, LoL, Valorant, etc.).
- `/league_of_legends`, `/cs2`, `/valorant`: Shows options for the selected game (upcoming games, past results, roster).
- `/proximos_jogos_[game]`: Fetches the next 5 upcoming matches for the specified game.
- `/ultimos_jogos_[game]`: Retrieves the last 5 match results for the specified game.
- `/jogadores_[game]`: Lists the current roster for the specified game.
- `/help`: Provides contact information and support options.

Example interaction:
1. Send `/start` to see game options.
2. Send `/cs2` to view CS2-specific options.
3. Send `/proximos_jogos_cs2` to get upcoming CS2 matches.

## File Structure
```
esports-chatbot/
├── chatbot.py              # Main bot logic and Telegram integration
├── get_cs2_info.py         # Functions to fetch CS2 data (roster, schedule)
├── get_lol_info.py         # Functions to fetch LoL data (roster, schedule)
├── get_valorant_info.py    # Functions to fetch Valorant data (roster, schedule)
├── logs/                   # Directory for log files
├── .env                    # Environment variables (not tracked)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

Please ensure your code follows the existing style and includes appropriate logging for errors.

Feel free to contact me in case of any doubt: theoalmeida00@gmail.com
