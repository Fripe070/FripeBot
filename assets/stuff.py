import discord
import json
import os

with open("config.json") as f:
    config = json.load(f)


class col:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'


# COGS  -----------------------------------------------------------------------------------
def getcogs(dir: str = None):
    COGS = []  # Makes a empty list named "COGS"

    if dir is None:  # If the "dir" variable is empty deafult it to "cogs"
        dir = "cogs"
    elif dir.startswith("cogs"):
        pass
    else:
        dir = f"cogs/{dir}"

    dir = dir.replace(".", "/")  # Replaces "." with "/"
    dir = dir.replace("\\", "/")  # Replaces "\" with "/"

    if os.path.isfile(f"{dir}.py"):  # If the path provided is a file (aka not a directory)
        return [dir.replace("\\", ".").replace("/", ".")]  # Replaces "\" and "/" with "." and returns the file

    for path, subdirs, files in os.walk(dir):  # For evcerything in the "dir" directory
        for filename in files:  # For all files in that directory
            if filename.endswith(".py"):  # Makes sure the file is actualy a python file
                # Adds the file to the list named "COGS"
                COGS.append(
                    (os.path.join(path, filename)
                     # Replaces "\" and "/" with "."
                     ).replace("\\", ".").replace("/", ".")[:-3])

    return COGS if COGS != [] else None


def getpfp(user: discord.User):
    return user.display_avatar.with_size(4096).with_static_format("png")


def splitstring(message, length=2000):
    return [message[i:i + length] for i in range(0, len(message), length)]


def securestring(oldstring):
    newstring = ""
    banned_chars = ["`", "*", "_", "~", "|", "<", ">"]
    for char in oldstring:
        if char in banned_chars:
            newstring += f"\{char}"
        else:
            newstring += char
    return newstring
