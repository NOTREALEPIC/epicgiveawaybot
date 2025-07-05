# === PYTHON 3.13 PATCH ===
import sys
import types
sys.modules['audioop'] = types.SimpleNamespace()  # Fix for Python 3.13.4 crash

# === Imports ===
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio, random, os, datetime

# === Bot Setup ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === Uptime Tracking ===
start_time = datetime.datetime.utcnow()
last_downtime = None
status_channel_id = 1385654852209610957  # 🔧 Replace with your uptime channel ID
status_message = None

def format_uptime(delta):
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days:02}:{hours:02}:{minutes:02}:{seconds:02}"

@tasks.loop(seconds=40)
async def update_uptime():
    global status_message
    now = datetime.datetime.utcnow()
    uptime = format_uptime(now - start_time)
    downtime = format_uptime(last_downtime) if last_downtime else "None"

    embed = discord.Embed(title="🟢 ZEBURE TEST", color=discord.Color.green())
    embed.add_field(name="⏱ Uptime", value=uptime, inline=True)
    embed.add_field(name="🛑 Last Downtime", value=downtime, inline=True)
    embed.set_footer(text="Updated every 40s")

    channel = bot.get_channel(status_channel_id)
    if not channel:
        return

    try:
        if not status_message:
            status_message = await channel.send(embed=embed)
        else:
            await status_message.edit(embed=embed)
    except discord.HTTPException as e:
        print(f"Failed to update uptime message: {e}")

@bot.event
async def on_connect():
    global start_time, last_downtime
    now = datetime.datetime.utcnow()
    if start_time:
        last_downtime = now - start_time
    start_time = now

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

    log_channel_id = 1385660621470830702  # 🔧 Replace with your logging channel ID
    view = GiveawayView(duration * 60, winners, log_channel_id)
    message = await channel.send(embed=embed, view=view)
    view.message = message

# === Bot Ready Event ===
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"⚠️ Sync Error: {e}")
    
    update_uptime.start()

# === Run the Bot ===
if __name__ == "__main__":
    TOKEN = os.getenv("BABU")  # ✅ Add your token as an env variable in Zeabur
    if not TOKEN:
        print("❌ Environment variable 'BABU' not found!")
        exit()
    bot.run(TOKEN)