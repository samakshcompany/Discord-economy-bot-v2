# ────────────────────────────────────────────────────────────────
# 💠 CX BOT — Always Online Version (Render Compatible)
# 🧠 Features: Prefix system | Blacklist | Error handling | Keep Alive | Cog Loader | Auto Presence
# 🧑‍💻 Made by: Code X Verse
# ────────────────────────────────────────────────────────────────

import discord
from discord.ext import commands
import os
import json
import asyncio
import logging
import sys
import traceback
import datetime
from keep_alive import keep_alive

# ──────────────── LOGGING SETUP ────────────────
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("discord.log", encoding="utf-8", mode="w"),
        logging.StreamHandler()
    ]
)

# ──────────────── DISCORD INTENTS ────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True


# ──────────────── PREFIX FUNCTION ────────────────
def get_prefix(bot, message):
    """A callable to retrieve prefixes for guilds."""
    try:
        with open("data/np_users.json", "r") as f:
            np_users = json.load(f)

        user_id = str(message.author.id)
        if user_id in np_users:
            user_data = np_users[user_id]
            if not user_data.get("active", False):
                return "cx "
            expires_at = user_data.get("expires_at", "lifetime")
            if expires_at != "lifetime":
                try:
                    expiry = datetime.datetime.fromisoformat(expires_at)
                    if expiry < datetime.datetime.now():
                        user_data["active"] = False
                        with open("data/np_users.json", "w") as f:
                            json.dump(np_users, f, indent=4)
                        return "cx "
                except (ValueError, TypeError):
                    return "cx "
            return ["", "cx "]
    except (FileNotFoundError, json.JSONDecodeError):
        if message.author.id == bot.owner_id:
            return ["", "cx "]

    if not message.guild:
        return "cx "

    try:
        with open("data/prefixes.json", "r") as f:
            prefixes = json.load(f)
        return prefixes.get(str(message.guild.id), "cx ")
    except (FileNotFoundError, json.JSONDecodeError):
        return "cx "


# ──────────────── BOT INITIALIZATION ────────────────
bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    case_insensitive=True,
    owner_id=1429162914543304794,
    help_command=None
)


# ──────────────── GLOBAL CHECKS ────────────────
@bot.check
async def globally_block_dms(ctx):
    """Block bot usage in DMs."""
    return ctx.guild is not None


@bot.check
async def check_if_blacklisted(ctx):
    """Globally checks if a user is blacklisted."""
    blacklist_file = "data/blacklist.json"
    if not os.path.exists(blacklist_file):
        return True

    with open(blacklist_file, 'r') as f:
        blacklist = json.load(f)

    if ctx.author.id in blacklist:
        await ctx.send("🚫 You are banned from using this bot. Join support for help: https://discord.gg/code-verse")
        return False
    return True


# ──────────────── ERROR HANDLER ────────────────
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        td = datetime.timedelta(seconds=error.retry_after)
        em = discord.Embed(
            title="⏳ Command on Cooldown",
            description=f"Please try again in **{td.seconds}s**.",
            color=discord.Color.red()
        )
        await ctx.send(embed=em, delete_after=5)

    elif isinstance(error, commands.MissingPermissions):
        em = discord.Embed(
            title="❌ Permission Denied",
            description="You don't have permission to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=em)

    elif isinstance(error, commands.MissingRequiredArgument):
        em = discord.Embed(
            title="⚠️ Missing Argument",
            description=f"You are missing a required argument.\nUsage: `cx {ctx.command.name} {ctx.command.signature}`",
            color=discord.Color.red()
        )
        await ctx.send(embed=em)

    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore invalid commands

    else:
        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


# ──────────────── READY EVENT ────────────────
@bot.event
async def on_ready():
    """Event that fires when the bot is connected and ready."""
    print(f"\n✅ Logged in as {bot.user.name} ({bot.user.id})")
    print("🌐 Connected to Discord API successfully!")
    print("💻 Made by Code X Verse → https://discord.gg/code-verse")
    print("─────────────────────────────────────────────")

    # Ensure data files exist
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.isfile('data/users.json'):
        with open('data/users.json', 'w') as f:
            json.dump({}, f)

    # Change bot status
    await bot.change_presence(activity=discord.Game(name="cx help | Managing the Economy"))


# ──────────────── COG LOADER ────────────────
async def load_cogs():
    """Loads all cogs from the 'cogs' directory."""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != 'emojis.py':
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"⚙️ Loaded cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load cog {filename}: {e}")


# ──────────────── MAIN LOOP ────────────────
async def main():
    """Main function to load cogs, keep alive, and run the bot."""
    keep_alive()  # Keeps the bot alive for Render
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        print("=" * 50)
        print("❌ CRITICAL: DISCORD_TOKEN not found in environment variables.")
        print("➡️ Create a file named `.env` and add this line:")
        print("DISCORD_TOKEN=YOUR_TOKEN_HERE")
        print("=" * 50)
        return

    async with bot:
        await load_cogs()
        await bot.start(token)


# ──────────────── ENTRY POINT ────────────────
if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ dotenv not found. Install it using: pip install python-dotenv")

    asyncio.run(main())
