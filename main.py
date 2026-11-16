import discord
from discord.ext import commands
import os
import random
import json
import aiohttp
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- CONFIG ---
MC_SERVER_IP = "play.blazemc.space"

# --- DATA SAVE ---
DATA_FILE = "data.json"
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"coins": {}, "xp": {}, "level": {}, "warns": {}}
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)
data = load_data()
def get_coins(uid): return data["coins"].get(str(uid), 0)
def add_coins(uid, amt):
    data["coins"][str(uid)] = get_coins(uid) + amt
    save_data(data)

# --- EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="!help_blaze | play.blazemc.space 🔥"))

@bot.event
async def on_message(message):
    if message.author.bot: return
    uid = str(message.author.id)
    add_coins(message.author.id, 1)
    data["xp"][uid] = data["xp"].get(uid, 0) + 5
    lvl = data["level"].get(uid, 1)
    if data["xp"][uid] >= lvl * 100:
        data["level"][uid] = lvl + 1
        await message.channel.send(f"🎉 {message.author.mention} Level **{lvl+1}** pe pahunch gaya! 🔥")
        save_data(data)
    await bot.process_commands(message)

# --- HELP ---
@bot.command()
async def help_blaze(ctx):
    embed = discord.Embed(title="🔥 BlazeMC Bot - All Commands", color=discord.Color.orange())
    embed.add_field(name="🎮 Minecraft", value="`!mcstatus` `!mcplayers` `!mcip` `!mcinfo`", inline=False)
    embed.add_field(name="💰 Economy", value="`!coins` `!daily` `!give @user 50` `!gamble 100` `!rob @user` `!leaderboard` `!shop` `!buy sword`", inline=False)
    embed.add_field(name="⭐ Level", value="`!level` `!rank`", inline=False)
    embed.add_field(name="🛡️ Moderation", value="`!kick` `!ban` `!unban` `!mute` `!unmute` `!warn` `!warnings` `!clear` `!lock` `!unlock` `!slowmode 5`", inline=False)
    embed.add_field(name="🎲 Fun", value="`!coinflip` `!dice` `!8ball` `!roast @user` `!meme` `!joke` `!love @user` `!ship @a @b`", inline=False)
    embed.add_field(name="🛠️ Utility", value="`!ping` `!avatar` `!userinfo` `!serverinfo` `!poll` `!say`", inline=False)
    await ctx.send(embed=embed)

# --- MINECRAFT STATUS ---
async def get_mc_status():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.mcsrvstat.us/2/{MC_SERVER_IP}", timeout=10) as r:
                return await r.json()
    except:
        return None

@bot.command(aliases=["mc", "status"])
async def mcstatus(ctx):
    d = await get_mc_status()
    if not d or not d.get("online"):
        return await ctx.send(f"🔴 **{MC_SERVER_IP} OFFLINE hai!** 😭 Server band hai!")
    embed = discord.Embed(title="🟢 BlazeMC - ONLINE!", color=discord.Color.green())
    embed.add_field(name="📡 IP", value=f"`{MC_SERVER_IP}`", inline=False)
    embed.add_field(name="👥 Players", value=f"**{d['players']['online']} / {d['players']['max']}** online", inline=True)
    embed.add_field(name="🎮 Version", value=d.get("version", "Unknown"), inline=True)
    embed.add_field(name="📝 MOTD", value=d.get("motd", {}).get("clean", ["BlazeMC"])[0], inline=False)
    if d['players']['online'] > 0 and d['players'].get("list"):
        embed.add_field(name="🔥 Online Players", value=", ".join(d['players']['list'][:15]), inline=False)
    embed.set_footer(text="BlazeMC | !mcstatus")
    await ctx.send(embed=embed)

@bot.command(aliases=["ip", "play"])
async def mcip(ctx):
    await ctx.send(f"🎮 **BlazeMC me join karo!**\n📡 IP: `{MC_SERVER_IP}`\n👉 Minecraft > Multiplayer > Add Server > Ye IP daal de!")
@bot.command(aliases=["players", "online"])
async def mcplayers(ctx):
    d = await get_mc_status()
    if not d or not d.get("online"): return await ctx.send("🔴 Server offline hai!")
    if d['players']['online'] == 0: return await ctx.send("😴 Abhi koi online nahi hai! Tu pehla ban ja!")
    await ctx.send(f"👥 **{d['players']['online']} Players Online:**\n```\n" + "\n".join(d['players'].get("list", [])) + "\n```")
@bot.command()
async def mcinfo(ctx):
    await ctx.send(f"🏰 **BlazeMC Info**\n📡 IP: `{MC_SERVER_IP}`\n🌐 Version: Java 1.20+\n🎮 Status: `!mcstatus`")

# --- ECONOMY ---
@bot.command()
async def coins(ctx): await ctx.send(f"💰 {ctx.author.mention} tere paas **{get_coins(ctx.author.id)}** coins hai!")
@bot.command(aliases=["balance"])
async def bal(ctx): await ctx.send(f"💰 {ctx.author.mention} Balance: **{get_coins(ctx.author.id)}** coins")
@bot.command()
async def daily(ctx):
    amt = random.randint(50, 150); add_coins(ctx.author.id, amt)
    await ctx.send(f"🎁 {ctx.author.mention} tujhe **{amt}** coins mile!")
@bot.command()
async def give(ctx, member: discord.Member, amount: int):
    if amount <= 0: return await ctx.send("❌ 0 se zyada likh!")
    if get_coins(ctx.author.id) < amount: return await ctx.send("❌ Coins kam hai!")
    add_coins(ctx.author.id, -amount); add_coins(member.id, amount)
    await ctx.send(f"✅ {ctx.author.mention} ne {member.mention} ko **{amount}** coins diye!")
@bot.command()
async def gamble(ctx, amount: int):
    if get_coins(ctx.author.id) < amount: return await ctx.send("❌ Coins kam hai!")
    if random.choice([True, False]):
        add_coins(ctx.author.id, amount); await ctx.send(f"🎉 Jeet gaya! **+{amount}** coins!")
    else:
        add_coins(ctx.author.id, -amount); await ctx.send(f"😭 Haar gaya! **-{amount}** coins!")
@bot.command()
async def rob(ctx, member: discord.Member):
    if random.choice([True, False]):
        amt = random.randint(10, 100); add_coins(member.id, -amt); add_coins(ctx.author.id, amt)
        await ctx.send(f"💸 {ctx.author.mention} ne {member.mention} se **{amt}** coins chura liye!")
    else: await ctx.send(f"🚨 Pakda gaya! {ctx.author.mention} rob nahi kar paya!")
@bot.command()
async def leaderboard(ctx):
    top = sorted(data["coins"].items(), key=lambda x: x[1], reverse=True)[:5]
    msg = "🏆 **Top 5 Richest:**\n"
    for i, (uid, coins) in enumerate(top, 1):
        user = await bot.fetch_user(int(uid)); msg += f"{i}. {user.name} - {coins} coins\n"
    await ctx.send(msg)
@bot.command()
async def shop(ctx): await ctx.send("🛒 **SHOP:**\n1. `!buy sword` - 500 coins\n2. `!buy shield` - 300 coins\n3. `!buy crown` - 1000 coins\n4. `!buy vip` - 5000 coins")
@bot.command()
async def buy(ctx, item: str):
    prices = {"sword": 500, "shield": 300, "crown": 1000, "vip": 5000}
    item = item.lower()
    if item not in prices: return await ctx.send("❌ Ye item nahi hai!")
    if get_coins(ctx.author.id) < prices[item]: return await ctx.send("❌ Coins kam hai!")
    add_coins(ctx.author.id, -prices[item]); await ctx.send(f"✅ {ctx.author.mention} ne **{item}** khareed liya! 🎉")
@bot.command()
async def level(ctx):
    uid = str(ctx.author.id); await ctx.send(f"⭐ {ctx.author.mention} Level: **{data['level'].get(uid, 1)}** | XP: **{data['xp'].get(uid, 0)}**")
@bot.command(aliases=["rank"])
async def rank_cmd(ctx): await level(ctx)

# --- MODERATION ---
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason); await ctx.send(f"👢 {member.mention} kicked! Reason: {reason}")
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason); await ctx.send(f"🔨 {member.mention} BANNED! Reason: {reason}")
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, name):
    for b in await ctx.guild.bans():
        if b.user.name == name:
            await ctx.guild.unban(b.user); return await ctx.send(f"✅ {b.user.mention} unban ho gaya!")
    await ctx.send("❌ Nahi mila!")
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount+1); await ctx.send(f"🧹 {amount} msg delete!", delete_after=3)
@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member):
    await member.timeout(discord.utils.utcnow() + timedelta(minutes=10)); await ctx.send(f"🔇 {member.mention} 10 min mute!")
@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None); await ctx.send(f"🔊 {member.mention} unmute!")
@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="Warn"):
    uid = str(member.id); data["warns"][uid] = data["warns"].get(uid, 0) + 1; save_data(data)
    await ctx.send(f"⚠️ {member.mention} Warn #{data['warns'][uid]} - {reason}")
@bot.command()
async def warnings(ctx, member: discord.Member): await ctx.send(f"⚠️ {member.mention} ke **{data['warns'].get(str(member.id), 0)}** warns hai!")
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx): await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False); await ctx.send("🔒 Channel lock!")
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx): await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True); await ctx.send("🔓 Channel unlock!")
@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, sec: int): await ctx.channel.edit(slowmode_delay=sec); await ctx.send(f"🐢 Slowmode {sec} sec set!")

# --- FUN ---
@bot.command()
async def coinflip(ctx): await ctx.send(f"🪙 {random.choice(['Heads!', 'Tails!'])}")
@bot.command()
async def dice(ctx): await ctx.send(f"🎲 {random.randint(1,6)} aaya!")
@bot.command(name="8ball")
async def eightball(ctx, *, q=""): await ctx.send(f"🎱 {random.choice(['Haan bilkul!', 'Nahi bhai', 'Pakka!', 'Sochna padega', '100% Haan', 'Bhul ja'])}")
@bot.command()
async def roast(ctx, member: discord.Member): await ctx.send(f"🔥 {member.mention}, {random.choice(['tera internet meri dadi se slow hai', 'tu to bot se bhi zyada boring hai', 'tera face dekh ke wifi disconnect ho gaya'])}")
@bot.command()
async def meme(ctx): await ctx.send(random.choice(["😂 Jab teacher bole homework nahi kiya...", "😂 Jab mummy bole phone rakh de...", "😂 Exam me sab aata hai, bas answer nahi aata"]))
@bot.command()
async def joke(ctx): await ctx.send(random.choice(["😂 Teacher: Late kyu? Student: Board pe likha tha 'School Ahead, Slow Down' to slow aa gaya!", "😂 Pappu: Mummy jhagda ho gaya! Mummy: Kis se? Pappu: Apne aap se, mirror me dekh ke!"]))
@bot.command()
async def love(ctx, member: discord.Member): await ctx.send(f"❤️ {ctx.author.mention} + {member.mention} = **{random.randint(0,100)}%** Love!")
@bot.command()
async def ship(ctx, a: discord.Member, b: discord.Member): await ctx.send(f"💘 {a.mention} ❤️ {b.mention} = **{random.randint(0,100)}%** Match!")

# --- UTILITY ---
@bot.command()
async def ping(ctx): await ctx.send(f"🏓 Pong! {round(bot.latency*1000)}ms")
@bot.command()
async def avatar(ctx, member: discord.Member = None):
    m = member or ctx.author; await ctx.send(m.display_avatar.url)
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    m = member or ctx.author; await ctx.send(f"👤 **{m.name}**\nID: {m.id}\nCoins: {get_coins(m.id)}")
@bot.command()
async def serverinfo(ctx):
    g = ctx.guild; await ctx.send(f"🏰 **{g.name}**\nMembers: {g.member_count}\nChannels: {len(g.channels)}")
@bot.command()
async def poll(ctx, *, q=""):
    msg = await ctx.send(f"📊 **POLL:** {q}\n✅ = Haan | ❌ = Nahi"); await msg.add_reaction("✅"); await msg.add_reaction("❌")
@bot.command()
async def say(ctx, *, text=""): await ctx.send(text)

# --- ERRORS ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions): await ctx.send("❌ Permission nahi hai!")
    elif isinstance(error, commands.MissingRequiredArgument): await ctx.send("❌ Sahi tarike se likh! `!help_blaze` dekh.")
    elif isinstance(error, commands.MemberNotFound): await ctx.send("❌ Banda nahi mila!")

# --- RUN ---
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ DISCORD_TOKEN missing!")
else:
    bot.run(TOKEN)
