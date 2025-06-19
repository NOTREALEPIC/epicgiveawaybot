import discord
from discord.ext import commands
import asyncio
from threading import Thread
from flask import Flask
import os

# ==== Flask App for Uptime ====
app = Flask(__name__)

@app.route('/')
def home():
    return "💖 EpicGiveaway Bot is running and ready to make you win, baby!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ==== Discord Bot ====
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} 💖")

# Load your cogs (like the giveaway one)
async def load_extensions():
    await bot.load_extension("giveaway")  # your giveaway.py file

# ==== Start Everything ====
if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    asyncio.run(load_extensions())
    TOKEN = os.environ.get("TOKEN") or "your_bot_token_here"
    bot.run(TOKEN)
