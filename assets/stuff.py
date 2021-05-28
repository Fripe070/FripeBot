# Imports
import discord, json, os, random
from discord.ext import commands
from discord.ext.commands import *
from dotenv import load_dotenv
from glob import glob
from traceback import format_exception
from assets.dynotags_formated import dynotags
from assets.deathmessages import *
from assets.en_us import en_us as mc_en_us
from assets.bannedwords import bannedwords

with open("config.json") as f:
    config = json.load(f)

with open('assets/dynotags.json', 'r') as f:
    dtags = json.load(f)

intents = discord.Intents.all()
prefix = config["prefixes"]
trusted = config["trusted"]
ownerid = 444800636681453568


bot = commands.Bot(
    command_prefix=prefix,
    case_insensitive=True,
    intents=intents,
    owner_id=ownerid
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
    BOLDOKBLUE = '\033[1m\033[94m'
    BOLDOKCYAN = '\033[1m\033[96m'
    BOLDOKGREEN = '\033[1m\033[92m'
    BOLDWARN = '\033[1m\033[93m'
    BOLDFAIL = '\033[1m\033[91m'


def rembackslash(text):  # Thanks Discord_
    e = list(text)
    bruh = []
    for unallowed in e:
        if unallowed == "`":
            bruh.append("\`")
        else:
            bruh.append(unallowed)
    return "".join(bruh)


# COGS  -----------------------------------------------------------------------------------
def getcogs(dir: str = ""):
    COGS = [] # Makes a list named "COGS" that is empty
    if dir == "":  # If the "dir" variable is empty deafult it to "cogs"
        dir = "cogs"
    dir = dir.replace(".", "/")  # Replaces "." with "/"
    dir = dir.replace("\\", "/")  # Replaces "\" with "/"
    if os.path.isfile(f"cogs/{dir}.py"):  # If the path provided is a file (aka not a directory)
        return [f"cogs.{dir}"]  # Just return that file
    for path, subdirs, files in os.walk(dir):  # For evcerything in the "dir" directory
        for filename in files:  # For all files in that directory
            if filename.endswith(".py"):  # Makes sure the file is actualy a python file
                # Adds the file to the list named "COGS"
                COGS.append(
                    (os.path.join(path, filename)
                     # Replaces "\" and "/" with "."
                     ).replace("\\", ".").replace("/", ".")[:-3])
    return COGS if COGS != [] else None


async def senderror(ctx, error):
    try:
        embed = discord.Embed(colour=0xff0000, timestamp=ctx.message.created_at,
                              title="An error occurred! Please notify Fripe if necessary.", description=f"```{error}```")
        embed.set_footer(text=f"Caused by {ctx.author}")
        await ctx.send(embed=embed)  # Send error in chat
    except Exception:  # When big oops happens (aka it fails to send the error in chat)
        print(f"{bcolors.WARNING + bcolors.BOLD}Failed to send chat message{bcolors.ENDC}")
    finally:  # Print error to console
        formatederror = "".join(format_exception(type(error), error, error.__traceback__)).rstrip()
        print(f"{bcolors.FAIL}{bcolors.ENDC + bcolors.FAIL}{formatederror}{bcolors.ENDC}")