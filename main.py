"""
BlazeMC - All In One Discord Bot
Features: Minecraft Status, Moderation, Level, Economy, Tickets, Fun
Server IP: play.blazemc.space (Java + Bedrock)
"""

import os
import random
import asyncio
import logging
from datetime import timedelta

import aiohttp
import discord
from discord.ext import commands

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

SERVER_IP = "play.blazemc.space"
COMMAND_PREFIX = "!"
BOT_ACTIVITY = "BlazeMC | !help | play.blazemc.space"
MEMBER_ROLE_NAME = "Members"

# In-memory storage (Restart hone par reset ho jayega)
# Production ke liye isko Database se replace karein
user_levels: dict[str, int] = {}
user_coins: dict[str, int] = {}

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlazeMC")

# --------------------------------------------------
# BOT SETUP
# --------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    intents=intents,
    help_command=None,
    case_insensitive=True
)

@bot.event
async def on_ready():
    """Bot jab online aaye tab chalega."""
    logger.info(f"Bot is online | Logged in as {bot.user}")
    await bot.change_presence(
        activity=discord.Game(name=BOT_ACTIVITY)
    )

@bot.event
async def on_message(message: discord.Message):
    """Level aur Economy ke liye har message par XP dena."""
    if message.author.bot:
        return

    user_id = str(message.author.id)
    user_levels[user_id] = user_levels.get(user_id, 0) + 1
    user_coins[user_id] = user_coins.get(user_id
