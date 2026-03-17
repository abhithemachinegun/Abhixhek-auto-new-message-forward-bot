# Telegram Auto-Forwarder Bot 🤖

This is a multi-user Telegram bot that forwards messages from a source channel to a target channel without the "Forwarded from" tag. 

Multiple users can connect their own bots to this main bot. It uses MongoDB to store user data and automatically resumes forwarding after any downtime.

## 🌟 Features
- **Tagless Forwarding:** Copies messages cleanly without the forward tag.
- **Multi-Bot Support:** Users can add their own bots via the main bot.
- **Auto-Resume:** Automatically processes missed messages if the bot goes offline.
- **Admin Controls:** Commands to ban/unban users, clear the database, and restart the bot.
- **User Logging:** Notifies the admin when a new user starts the bot.

## 🛠️ Environment Variables
To deploy this bot on Koyeb, Render, or Heroku, you need to set the following Environment Variables (Config Vars):

* `API_ID` : Your Telegram API ID (from my.telegram.org)
* `API_HASH` : Your Telegram API Hash (from my.telegram.org)
* `BOT_TOKEN` : The Main Bot Token (from @BotFather)
* `MONGO_URI` : Your MongoDB connection string (from MongoDB Atlas)
* `ADMIN_ID` : Your personal Telegram User ID (for admin commands)
* `LOG_CHANNEL` : The ID of the channel where new user logs will be sent (e.g., -100123456789)

## 💻 Admin Commands
- `/ban [User ID]` - Ban a user from using the bot.
- `/unban [User ID]` - Unban a user.
- `/cleanmongo` - Wipes all database records (stops all child bots).
- `/restart` - Restarts the main script.
- 
