# === PATCH for Python 3.13.4 (no audio use) ===
import sys, types
sys.modules['audioop'] = types.SimpleNamespace()

# === Imports ===
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio, random, os
from datetime import datetime
import pytz
from threading import Thread
from flask import Flask

# === Flask Keepalive Server ===
app = Flask("epic-bot")

@app.route("/")
def home():
    return "EPIC GIVEAWAY BOT ONLINE ✅"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# === Discord Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === Uptime Embed ===
tz = pytz.timezone("Asia/Kolkata")
start_time = datetime.now(tz)
status_channel_id = 1391327447764435005
status_message_id = int(os.getenv("UPTIME_MSG_ID", "0"))
status_message = None

def format_uptime(delta):
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days:02}d:{hours:02}h:{minutes:02}m:{seconds:02}s"

@tasks.loop(seconds=20)
async def update_uptime():
    global status_message
    now = datetime.now(tz)
    uptime = format_uptime(now - start_time)
    last_update = now.strftime("%I:%M:%S %p IST")
    started = start_time.strftime("%I:%M %p IST")

    embed = discord.Embed(title="🎉 EPIC GIVEAWAY BOT", color=discord.Color.green())
    embed.add_field(name="START", value=f"```{started}```", inline=False)
    embed.add_field(name="UPTIME", value=f"```{uptime}```", inline=False)
    embed.add_field(name="LAST UPDATE", value=f"```{last_update}```", inline=False)

    channel = bot.get_channel(status_channel_id)
    if not channel:
        return
    try:
        if not status_message:
            status_message = await channel.fetch_message(status_message_id)
        await status_message.edit(embed=embed)
    except Exception as e:
        print(f"❌ Uptime update error: {e}")

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
            await interaction.response.send_message("❌ You already entered!", ephemeral=True)
        else:
            self.participants.add(interaction.user.id)
            await interaction.response.send_message("✅ You're in!", ephemeral=True)
            log_channel = interaction.client.get_channel(self.log_channel_id)
            if log_channel:
                await log_channel.send(f"{interaction.user.mention} entered the giveaway!")

    async def on_timeout(self):
        if self.message:
            await self.announce_winners()

    async def announce_winners(self):
        embed = self.message.embeds[0]
        if len(self.participants) < self.winners_count:
            result = "❌ Not enough participants."
        else:
            winners = random.sample(list(self.participants), self.winners_count)
            result = f"🎊 Winners: {', '.join(f'<@{uid}>' for uid in winners)}"
        embed.add_field(name="🏁 Ended", value=result, inline=False)
        await self.message.edit(embed=embed, view=None)

# === Slash Commands ===

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
        description=f"@LEGIT\n**Item**: {item}\n**Sponsor**: {sponsor}\n**Duration**: {duration} min\n**Winners**: {winners}\nClick to enter!",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Started by {interaction.user.display_name}")
    embed.timestamp = discord.utils.utcnow()

    log_channel_id = 1385660621470830702
    view = GiveawayView(duration * 60, winners, log_channel_id)
    message = await channel.send(embed=embed, view=view)
    view.message = message

@bot.tree.command(name="say", description="Send dummy embed to channel")
@app_commands.describe(channel="Channel to send embed")
async def say(interaction: discord.Interaction, channel: discord.TextChannel):
    roles = [r.name.lower() for r in interaction.user.roles]
    if not any(role in roles for role in ['admin', 'mod', 'root']):
        await interaction.response.send_message("❌ No permission!", ephemeral=True)
        return
    embed = discord.Embed(title="📢 Dummy Embed", description="This is a test embed.", color=discord.Color.orange())
    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Sent to {channel.mention}", ephemeral=True)

# === Events ===
@bot.event
async def on_connect():
    global start_time
    start_time = datetime.now(tz)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} commands.")
    except Exception as e:
        print(f"⚠️ Sync failed: {e}")
    update_uptime.start()

# === Run the Bot ===
if __name__ == "__main__":
    keep_alive()  # Start Flask server
    TOKEN = os.getenv("BABU")
    if not TOKEN:
        print("❌ BOT TOKEN not found (env: BABU)")
        exit()
    bot.run(TOKEN)
