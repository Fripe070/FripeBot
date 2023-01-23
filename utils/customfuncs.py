import json


# TODO: These are both quite useless, so I'll delete/remake them at another time


def disable_commands(bot) -> list[str]:
    with open("config.json") as f:
        return [command for command in bot.commands if command not in json.load(f)["disabled_commands"]]


def splitstring(message, length=2000):
    return [message[i : i + length] for i in range(0, len(message), length)]
