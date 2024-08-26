import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Path to the JSON file
DATA_FILE = "user_data.json"

# Load data from JSON file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Save data to JSON file
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

user_data = load_data()

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if "bump done" in message.content.lower() and message.author.id == 302050872383242240:
        user = message.author
        user_id = str(user.id)  # Store user ID as string for JSON ??? 

        if user_id not in user_data:
            user_data[user_id] = {"points": 0, "streak": 0}

        user_data[user_id]["streak"] += 1

        if user_data[user_id]["streak"] == 3:
            user_data[user_id]["points"] += 2
            user_data[user_id]["streak"] = 0
        else:
            user_data[user_id]["points"] += 1

        save_data(user_data)

        await message.channel.send(f"{user.mention} has been awarded points! Total points: {user_data[user_id]['points']}")

    await bot.process_commands(message)

@bot.command(name='points')
async def check_points(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user_id = str(member.id)

    if user_id in user_data:
        points = user_data[user_id]["points"]
        await ctx.send(f"{member.mention} has {points} points.")
    else:
        await ctx.send(f"{member.mention} has no points yet.")

bot.run('YOUR_BOT_TOKEN')
