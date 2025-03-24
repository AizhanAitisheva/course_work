cineBob - Movie Recommendation Telegram Bot
This Telegram bot provides movie recommendations based on data from the imdb_movies.csv dataset, which was taken from Kaggle. The bot supports several commands to get recommendations, view popular movies, select a random movie, and look up for available genres.
Commands
•	/recommend — Get a movie recommendation.
•	/genres — View all available genres.
•	/popular — View the most popular movies.
•	/random — Get a random movie recommendation.
How to use our bot
1.	Find the bot in Telegram:
o	Search for the bot by its username (@cineBobbot) in Telegram.
2.	Start the bot:
o	Use the /start command to begin interactions with the bot.
3.	Use the commands:
o	Use commands /recommend, /genres, /popular, and /random to get movie recommendations.
Libraries Used
•	os — for working with the operating system.
•	logging — for logging.
•	random — for generating random numbers.
•	pandas — for data manipulation.
•	numpy — for numerical operations.
•	telegram — for interacting with the Telegram API.
•	telegram.ext — for creating command and message handlers.
Project Structure

course_work/
│
├── main.py                # Main bot script
├── imdb_movies.csv       # Movie dataset
├── README.md             # This file
└── .venv                  # Environment variables file
Example Usage
1.	Start the bot and find it in Telegram.
2.	Use the /start command to begin interacting.
3.	Use commands like /recommend, /genres, /popular, and /random to get movie recommendations.
________________________________________
[readme.docx](https://github.com/user-attachments/files/19429081/readme.docx)

