import discord
from discord.ext import commands
import os
import json
import random

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- DATA SAVE ---
user_coins = {}
user_levels = {}

# Agar pehle se data hai to load karo
try:
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            data = json.load(f)
            user_coins = data.get("coins", {})
            user_levels = data.get("levels", {})
except:
    user_coins = {}
    user_levels = {}

def save_data():
    try:
        with open("data.json", "w") as f:
            json.dump({"coins": user_coins, "levels": user_levels}, f)
    except:
        pass

# --- BOT READY ---
@bot.event
async def on_ready():
    print(f"Bot Online Hai: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="BlazeMC | !help"))

# --- LEVEL + COINS SYSTEM (FIXED) ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)

    # Level badhao
    user_levels[user_id] = user_levels.get(user_id, 0) + 1
    # Coins badhao - YE LINE PEHLE GALAT THI, AB FIXED HAI
    user_coins[user_id] = user_coins.get(user_id, 0) + 1

    # Har 100 message pe level up msg
    if user_levels[user_id] % 100 == 0:
        await message.channel.send(f"🔥 {message.author.mention} Level Up! Ab tum Level {user_levels[user_id] // 100} pe ho!")

    save_data()
    await bot.process_commands(message)

# --- COMMANDS ---
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! 🏓 {round(bot.latency * 1000)}ms")

@bot.command()
async def coins(ctx):
    user_id = str(ctx.author.id)
    coins = user_coins.get(user_id, 0)
    await ctx.send(f"💰 {ctx.author.mention} Tumhare paas **{coins} coins** hai!")

@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    coins = user_coins.get(user_id, 0)
    await ctx.send(f"💰 {ctx.author.mention} Balance: **{coins} coins**")

@bot.command()
async def level(ctx):
    user_id = str(ctx.author.id)
    lvl = user_levels.get(user_id, 0)
    await ctx.send(f"⭐ {ctx.author.mention} Tumhara XP: **{lvl}** | Level: **{lvl // 100}**")

@bot.command()
async def daily(ctx):
    user_id = str(ctx.author.id)
    reward = random.randint(50, 150)
    user_coins[user_id] = user_coins.get(user_id, 0) + reward
    save_data()
    await ctx.send(f"🎁 {ctx.author.mention} Daily Reward! Tumhe **{reward} coins** mile!")

@bot.command()
async def leaderboard(ctx):
    if not user_coins:
        await ctx.send("Abhi koi coins nahi hai!")
        return
    sorted_users = sorted(user_coins.items(), key=lambda x: x[1], reverse=True)[:5]
    msg = "🏆 **BlazeMC Top 5 Richest** 🏆\n"
    for i, (uid, coins) in enumerate(sorted_users, 1):
        msg += f"{i}. <@{uid}> - {coins} coins\n"
    await ctx.send(msg)

@bot.command()
async def help_blaze(ctx):
    await ctx.send("**BlazeMC Bot Commands:**\n`!ping` - Ping check\n`!coins` / `!balance` - Coins dekho\n`!level` - Level dekho\n`!daily` - Daily coins lo\n`!leaderboard` - Top 5 dekho")

# --- BOT RUN ---
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("ERROR: DISCORD_TOKEN nahi mila Railway Variables me!")
else:
    bot.run(TOKEN)
