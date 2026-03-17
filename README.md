To deploy this on Koyeb, Heroku, or Render, you'll need to input these variables in their respective "Environment Variables" or "Config Vars" settings panels:
API_ID: Get this from my.telegram.org. It will be a number.
API_HASH: Get this from my.telegram.org. It will be a string of letters and numbers.
BOT_TOKEN: The token for your main control bot, obtained from @BotFather.
MONGO_URI: Your MongoDB connection string (get a free one from MongoDB Atlas). E.g., mongodb+srv://<username>:<password>@cluster.mongodb.net/
ADMIN_ID: Your personal Telegram User ID (get it from a bot like @userinfobot) so you can use the /ban, /restart, and /cleanmongo commands.
LOG_CHANNEL: The ID of the channel where you want new user logs to go (e.g., -100123456789). Make sure your main bot is an admin in this log channel.
# Abhixhek-auto-new-message-forward-bot
