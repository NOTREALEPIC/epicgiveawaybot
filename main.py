import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import asyncio, random, os

# === Flask Setup for Uptime ===
app = Flask(__name__)

@app.route('/')
def home():
    return "💖 EpicGiveaway Bot is running!"

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
            await interaction.response.send_message("You've already entered!", ephemeral=True)
        else:
            self.participants.add(interaction.user.id)
            await interaction.response.send_message("You're entered! Good luck 💖", ephemeral=True)
            log_channel = interaction.client.get_channel(self.log_channel_id)
            if log_channel:
                await log_channel.send(f"{interaction.user.mention} entered the giveaway!")

    async def on_timeout(self):
        if self.message:
            await self.announce_winners()

    async def announce_winners(self):
        embed = self.message.embeds[0]
        if len(self.participants) < self.winners_count:
            result = "Not enough participants to select winners."
        else:
            winners = random.sample(list(self.participants), self.winners_count)
            result = f"🎊 Congratulations: {', '.join(f'<@{uid}>' for uid in winners)}"

        embed.add_field(name="🎁 Giveaway Ended", value=result, inline=False)
        await self.message.edit(embed=embed, view=None)

# === Slash Command ===
@bot.tree.command(name="epicgiveaway", description="Start a fun giveaway 🎉")
@app_commands.describe(
    title="Giveaway Title",
    sponsor="Who is sponsoring?",
    duration="Duration in minutes",
    item="Giveaway Item",
    winners="Number of winners",
    channel="Channel to post giveaway in"
)
async def epicgiveaway(interaction: discord.Interaction,
                       title: str,
                       sponsor: str,
                       duration: int,
                       item: str,
                       winners: int,
                       channel: discord.TextChannel):
    
    await interaction.response.send_message(f"Giveaway started in {channel.mention}! 🎉", ephemeral=True)

    embed = discord.Embed(
        title=f"🎉 {title} 🎉",
        description=f"**Item**: {item}\n**Sponsor**: {sponsor}\n**Duration**: {duration} min\n**Winners**: {winners}\nClick the button below to enter 💖",
        color=discord.Color.pink()
    )
    embed.set_footer(text=f"Hosted by {interaction.user.display_name}")
    embed.timestamp = discord.utils.utcnow()

    log_channel_id = 123456789012345678  # 🔧 CHANGE to your log channel ID
    view = GiveawayView(duration * 60, winners, log_channel_id)
    message = await channel.send(embed=embed, view=view)
    view.message = message

# === Ready & Start ===
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Sync error: {e}")

# === Start Everything ===
if __name__ == "__main__":
    Thread(target=run_flask).start()
    TOKEN = os.environ.get("TOKEN") or "your_bot_token_here"  # replace for local test
    bot.run(TOKEN)
