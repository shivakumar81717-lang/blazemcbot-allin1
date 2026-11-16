import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
from mcrcon import MCRcon
import yt_dlp
import asyncio
import datetime

# --- BLAZEMC CONFIGURATION ---
TOKEN = "YOUR_DISCORD_BOT_TOKEN"       # Apna Bot Token dalein
PREFIX = "!"
SERVER_NAME = "BlazeMc"
MC_IP = "play.blazemc.space"
MC_PORT = 25565
RCON_PORT = 25575
RCON_PASSWORD = "YOUR_RCON_PASSWORD"   # server.properties wala RCON password
STATUS_CHANNEL_ID = 1571889388642631770 # Apne Status Channel ki ID dalein (bina quotes ke)

# Intents Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Music Setup
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True
}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

status_message_id = None

@bot.event
async def on_ready():
    print(f'✅ {SERVER_NAME} Bot Online hai: {bot.user.name}')
    if not update_server_status.is_running():
        update_server_status.start()

# --- 1. LIVE SERVER STATUS & PLAYER COUNT ---
@tasks.loop(seconds=30)
async def update_server_status():
    global status_message_id
    channel = bot.get_channel(STATUS_CHANNEL_ID)
    if not channel:
        return

    try:
        server = await JavaServer.async_lookup(f"{MC_IP}:{MC_PORT}")
        status = await server.async_status()
        
        await bot.change_presence(activity=discord.Game(name=f"{SERVER_NAME}: {status.players.online}/{status.players.max} Players"))

        embed = discord.Embed(
            title=f"🔥 {SERVER_NAME} Status: ONLINE 🟢",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="🌐 Server IP", value=f"`{MC_IP}`", inline=True)
        embed.add_field(name="👥 Players", value=f"**{status.players.online} / {status.players.max}**", inline=True)
        embed.add_field(name="🎮 Version", value=f"{status.version.name}", inline=True)
        embed.set_footer(text=f"{SERVER_NAME} • Live Auto-Updating Status")

    except Exception:
        await bot.change_presence(activity=discord.Game(name=f"{SERVER_NAME}: Offline 🔴"))
        embed = discord.Embed(
            title=f"🔥 {SERVER_NAME} Status: OFFLINE 🔴",
            description=f"**{SERVER_NAME}** abhi band hai ya maintenance mein hai.",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

    if status_message_id:
        try:
            msg = await channel.fetch_message(status_message_id)
            await msg.edit(embed=embed)
            return
        except discord.NotFound:
            pass

    sent_msg = await channel.send(embed=embed)
    status_message_id = sent_msg.id

# --- IP COMMAND (!ip) ---
@bot.command(name="ip")
async def server_ip(ctx):
    embed = discord.Embed(
        title=f"🔥 Join {SERVER_NAME} Now!",
        description="Neeche diye gaye IP se server join karein:",
        color=discord.Color.orange()
    )
    embed.add_field(name="Java IP", value=f"`{MC_IP}`", inline=True)
    embed.add_field(name="Port", value=f"`{MC_PORT}`", inline=True)
    embed.set_footer(text=f"Enjoy playing on {SERVER_NAME}!")
    await ctx.reply(embed=embed)

# --- 2. DISCORD SE SERVER MANAGE KAREIN (RCON) ---
@bot.command(name="cmd")
@commands.has_permissions(administrator=True)
async def rcon_command(ctx, *, mc_command: str):
    try:
        with MCRcon(MC_IP, RCON_PASSWORD, port=RCON_PORT) as mcr:
            response = mcr.command(mc_command)
            await ctx.reply(f"✅ **Command Executed:** `/{mc_command}`\n**Server Response:** {response or 'Done!'}")
    except Exception as e:
        await ctx.reply("❌ Server se RCON connect nahi ho paya. Check karein ki server on hai aur RCON enabled hai.")

# --- 3. MODERATION COMMANDS (!ban & !timeout) ---
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, member: discord.Member, *, reason="Koi reason nahi diya gaya"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 **{member}** ko **{SERVER_NAME}** Discord se ban kar diya gaya hai. | Reason: *{reason}*")

@bot.command(name="timeout")
@commands.has_permissions(moderate_members=True)
async def timeout_member(ctx, member: discord.Member, minutes: int, *, reason="Rules todne par timeout"):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"⏳ **{member}** ko **{minutes} minutes** ke liye timeout diya gaya hai. | Reason: *{reason}*")

# --- 4. COMMUNITY ENGAGEMENT (!suggest) ---
@bot.command(name="suggest")
async def suggest(ctx, *, suggestion: str):
    embed = discord.Embed(
        title=f"💡 {SERVER_NAME} Suggestion",
        description=suggestion,
        color=discord.Color.gold(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

# --- 5. MUSIC COMMANDS (!play, !skip, !stop) ---
@bot.command(name="play")
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.reply("⚠️ Pehle kisi Voice Channel mein join karein!")

    voice_channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)

    await ctx.reply(f"🔎 Search kiya ja raha hai: **{search}**...")

    
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{search}", download=False))
    
    if 'entries' in data and len(data['entries']) > 0:
        song = data['entries'][0]
        url = song['url']
        title = song['title']

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        source = discord.FFmpegPCMAudio(url, **ffmpeg_options)
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 Ab baj raha hai: **{title}**")
    else:
        await ctx.reply("❌ Koi gaana nahi mila.")

@bot.command(name="skip")
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.reply("⏭️ Gaana skip kar diya gaya hai!")
    else:
        await ctx.reply("❌ Abhi koi gaana nahi baj raha hai.")

@bot.command(name="stop")
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.reply("⏹️ Music band kar diya gaya hai aur bot voice channel se nikal gaya hai.")
    else:
        await ctx.reply("❌ Bot kisi voice channel mein nahi hai.")

# --- 6. GAME AUR DISCORD CHAT SYNC (DiscordSRV) ---
# Apne Minecraft Server ke 'plugins' folder mein DiscordSRV plugin dalein.
# Uske config.yml mein apna same Bot TOKEN aur Sync Channel ID dal dein.
# DiscordSRV bina kisi extra Python code ke chat sync handle kar lega.

bot.run(TOKEN)
        
