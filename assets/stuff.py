# Imports
import discord
import json
import os
import random
from discord.ext import commands
from discord.ext.commands import *
from dotenv import load_dotenv
from traceback import format_exception
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

hellowords = ["hello", "hi", "greetings", "howdy", "hey", "yo", "ello",
              "hallo", "hej", "tjena", "sup", "wassup", "god dag", "hallå", "holla"]

COGS = []
for cog in os.listdir("COGS"):
    if cog.endswith(".py"):
        COGS.append(cog[:-3])

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
