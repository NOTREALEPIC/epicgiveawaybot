# === PYTHON 3.13 PATCH ===
import sys
import types
sys.modules['audioop'] = types.SimpleNamespace()  # Fix for Python 3.13.4 crash

# === Imports ===
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import asyncio, random, os

# === Flask Web Server for Render Uptime ===
app = Flask(__name__)
@app.route('/')
def home():
    return "💖 EpicGiveaway Bot running on Python 3.13.4 (audioop patched)"
def run_flask():
    app.run(host='0.0.0.0', port=8080)

# === Discord Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === Giveaway View ===
class GiveawayView(discord.ui.View):
    def __init__(self, duration_sec, winners_count, log_channel_id):
        super().__init__(timeout=duration_sec)
        self.participants = set()
        self.winners_count = winners_count
        self.log_channel_id = log_channel_id
        self.message = None

    @discord.ui.button(label="🎉 Enter Giveaway", style=discord.ButtonStyle.green)
    async def enter_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.participants:
            await interaction.response.send_message("❌ You've already entered!", ephemeral=True)
        else:
            self.participants.add(interaction.user.id)
            await interaction.response.send_message("✅ You're entered! Good luck 💖", ephemeral=True)
            log_channel = interaction.client.get_channel(self.log_channel_id)
            if log_channel:
                await log_channel.send(f"{interaction.user.mention} entered the giveaway!")

    async def on_timeout(self):
        if self.message:
            await self.announce_winners()

    async def announce_winners(self):
        embed = self.message.embeds[0]
        if len(self.participants) < self.winners_count:
            result = "❌ Not enough participants to choose winners."
        else:
            winners = random.sample(list(self.participants), self.winners_count)
            result = f"🎊 Winner(s): {', '.join(f'<@{uid}>' for uid in winners)}"
        embed.add_field(name="🏁 Giveaway Ended", value=result, inline=False)
        await self.message.edit(embed=embed, view=None)

# === Slash Command ===
@bot.tree.command(name="epicgiveaway", description="Start a giveaway 🎁")
@app_commands.checks.has_role("MOD")
@app_commands.describe(
    title="Giveaway Title",
    sponsor="Sponsor Name",
    duration="Duration in minutes",
    item="Giveaway Item",
    winners="Number of winners",
    channel="Channel to post the giveaway"
)
async def epicgiveaway(interaction: discord.Interaction,
                       title: str,
                       sponsor: str,
                       duration: int,
                       item: str,
                       winners: int,
                       channel: discord.TextChannel):
    await interaction.response.send_message(f"🎉 Giveaway started in {channel.mention}!", ephemeral=True)

    embed = discord.Embed(
        title=f"🎉 {title} 🎉",
        description=f"@LEGIT\n**Item**: {item}\n**Sponsor**: {sponsor}\n**Duration**: {duration} min\n**Winners**: {winners}\n\nClick the button below to enter!",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Started by {interaction.user.display_name}")
    embed.timestamp = discord.utils.utcnow()

    log_channel_ids = [1385654852209610957, 1385660621470830702]  # 🔧 Replace with your logging channel IDs
    view = GiveawayView(duration * 60, winners, log_channel_id)
    message = await channel.send(embed=embed, view=view)
    view.message = message

# === Bot Events ===
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"⚠️ Sync Error: {e}")

# === Run Everything ===
if __name__ == "__main__":
    Thread(target=run_flask).start()
    ASMR = os.environ.get("BABU")
    bot.run(ASMR)
