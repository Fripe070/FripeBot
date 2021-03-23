# Imports
import discord
import os
import sys
import json
from discord.ext import commands
from discord.ext.commands import *
from dotenv import load_dotenv

with open("config.json") as f:
    config = json.load(f)

prefix = config["prefixes"]
trusted = config["trusted"]
ownerid = 444800636681453568

bot = commands.Bot(
    command_prefix=prefix,
    case_insensitive=True,
)

status = f'you. And {len(bot.guilds)} servers 👀'







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