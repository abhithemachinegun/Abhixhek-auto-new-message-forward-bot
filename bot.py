import os
import sys
import asyncio

# --- FIX FOR NEWER PYTHON VERSIONS (Render/Koyeb) ---
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
# ----------------------------------------------------

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from motor.motor_asyncio import AsyncIOMotorClient

# --- ENVIRONMENT VARIABLES ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URI = os.environ.get("MONGO_URI", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", 0))

# --- DATABASE SETUP ---
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["AutoForwarderBot"]
users_col = db["users"]
bots_col = db["child_bots"]
banned_col = db["banned_users"]

# --- MAIN BOT INITIALIZATION ---
app = Client("MainBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dictionary to keep track of running child bots
active_bots = {}

# --- HELPER FUNCTIONS ---
async def is_banned(user_id):
    user = await banned_col.find_one({"user_id": user_id})
    return bool(user)

async def start_child_bot(token, source_id, target_id):
    if token in active_bots:
        return
    
    # Initialize child bot
    child_app = Client(f"child_{token[:8]}", api_id=API_ID, api_hash=API_HASH, bot_token=token)
    
    @child_app.on_message(filters.chat(source_id))
    async def forward_without_tag(client, message):
        try:
            # .copy() sends the message without the "Forwarded from" tag
            await message.copy(target_id)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.copy(target_id)
        except Exception as e:
            print(f"Error forwarding message: {e}")

    await child_app.start()
    active_bots[token] = child_app

# --- MAIN BOT COMMANDS ---

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id
    if await is_banned(user_id):
        return await message.reply("You are banned from using this bot.")
    
    # Log new users
    existing_user = await users_col.find_one({"user_id": user_id})
    if not existing_user:
        await users_col.insert_one({"user_id": user_id, "username": message.from_user.username})
        log_text = f"**New User Started The Bot!**\n\n**ID:** `{user_id}`\n**Name:** {message.from_user.mention}"
        await app.send_message(LOG_CHANNEL, log_text)

    await message.reply(
        "Welcome to the Auto-Forwarder Bot!\n\n"
        "To add your own bot, use the following format:\n"
        "`/addbot BOT_TOKEN SOURCE_CHANNEL_ID TARGET_CHANNEL_ID`\n\n"
        "*Make sure your bot is an admin in both the source and target channels.*"
    )

@app.on_message(filters.command("addbot") & filters.private)
async def add_bot_cmd(client, message):
    if await is_banned(message.from_user.id):
        return
    
    args = message.command
    if len(args) != 4:
        return await message.reply("Invalid format! Use:\n`/addbot BOT_TOKEN SOURCE_CHANNEL_ID TARGET_CHANNEL_ID`")
    
    token, source, target = args[1], args[2], args[3]
    
    try:
        source = int(source)
        target = int(target)
    except ValueError:
        return await message.reply("Channel IDs must be numbers (e.g., -100123456789).")

    # Save to database
    await bots_col.update_one(
        {"token": token}, 
        {"$set": {"owner_id": message.from_user.id, "source_id": source, "target_id": target}}, 
        upsert=True
    )
    
    await message.reply("Starting your bot... Please wait.")
    
    try:
        await start_child_bot(token, source, target)
        await message.reply("✅ Your bot has been successfully connected and is now listening for messages!")
    except Exception as e:
        await message.reply(f"❌ Failed to start bot. Check your token and make sure it's an admin in the channels.\nError: `{str(e)}`")

# --- ADMIN COMMANDS ---

@app.on_message(filters.command("ban") & filters.user(ADMIN_ID))
async def ban_user(client, message):
    if len(message.command) < 2:
        return await message.reply("Provide a user ID to ban.")
    try:
        target_id = int(message.command[1])
        await banned_col.insert_one({"user_id": target_id})
        await message.reply(f"User `{target_id}` has been banned.")
    except Exception as e:
        await message.reply(f"Error: {e}")

@app.on_message(filters.command("unban") & filters.user(ADMIN_ID))
async def unban_user(client, message):
    if len(message.command) < 2:
        return await message.reply("Provide a user ID to unban.")
    try:
        target_id = int(message.command[1])
        await banned_col.delete_one({"user_id": target_id})
        await message.reply(f"User `{target_id}` has been unbanned.")
    except Exception as e:
        await message.reply(f"Error: {e}")

@app.on_message(filters.command("cleanmongo") & filters.user(ADMIN_ID))
async def clean_mongo(client, message):
    await db.drop_collection("users")
    await db.drop_collection("child_bots")
    await db.drop_collection("banned_users")
    active_bots.clear()
    await message.reply("✅ MongoDB storage cleared successfully. All child bots stopped.")

@app.on_message(filters.command("restart") & filters.user(ADMIN_ID))
async def restart_bot(client, message):
    await message.reply("Restarting bot...")
    os.execl(sys.executable, sys.executable, *sys.argv)

# --- STARTUP ROUTINE ---
async def main():
    print("Starting main bot...")
    await app.start()
    
    print("Loading child bots from database...")
    cursor = bots_col.find({})
    async for bot_data in cursor:
        try:
            await start_child_bot(bot_data["token"], bot_data["source_id"], bot_data["target_id"])
            print(f"Started child bot: {bot_data['token'][:8]}...")
        except Exception as e:
            print(f"Failed to start a child bot: {e}")
            
    print("All bots are running!")
    from pyrogram import idle
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
    
