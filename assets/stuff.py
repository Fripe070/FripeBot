# Imports
import discord, json, os, random
from discord.ext import commands
from discord.ext.commands import *
from dotenv import load_dotenv
from traceback import format_exception
from bannedwords import bannedwords
from assets.dynotags_formated import dynotags
from assets.deathmessages import *
from assets.en_us import en_us
from assets.bannedwords import bannedwords

with open("config.json") as f:
    config = json.load(f)

"""with open("assets/tags.json", "r") as f:
    dynotags = json.load(f)"""

intents = discord.Intents.all()
prefix = config["prefixes"]
trusted = config["trusted"]
ownerid = 444800636681453568
debug = config["debug"].lower()
COGS = []
for cog in os.listdir("COGS"):
    if cog.endswith(".py"):
        COGS.append(cog[:-3])
#COGS = ["admin", "utility", "voice", "fun"]

bot = commands.Bot(
    command_prefix=prefix,
    case_insensitive=True,
    intents=intents,
    owner_id=ownerid,
    help_command=None
)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'