import discord
import json
import os
import pathlib

from main import config


class col:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ITALIC = "\033[3m"


# COGS  -----------------------------------------------------------------------------------


def disable_commands(bot) -> list[str]:
    return [command for command in bot.commands if command not in config["disabled_commands"]]


def getpfp(user: discord.User):
    return user.display_avatar.with_size(4096).with_static_format("png")


def splitstring(message, length=2000):
    return [message[i : i + length] for i in range(0, len(message), length)]


def securestring(oldstring):
    newstring = ""
    banned_chars = ["`", "*", "_", "~", "|", "<", ">"]
    for char in oldstring:
        if char in banned_chars:
            newstring += f"\{char}"
        else:
            newstring += char
    return newstring
