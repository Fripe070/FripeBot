import json
import random
from pathlib import Path


def disable_commands(bot) -> list[str]:
    with open("config.json") as f:
        return [command for command in bot.commands if command not in json.load(f)["disabled_commands"]]


def splitstring(message, length=2000):
    return [message[i : i + length] for i in range(0, len(message), length)]


def get_cogs(cog_path: str) -> list[str]:
    cog_path = Path(cog_path)

    if not cog_path.is_dir():
        return [Path(cog_path).with_suffix("").as_posix().replace("/", ".")]

    return [(path.with_suffix("").as_posix().replace("/", ".")) for path in cog_path.rglob("*.py")]


def randomstring(length=0, key="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_0123456789"):
    return "".join(random.choice(key) for _ in range(length))
