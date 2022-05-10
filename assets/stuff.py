from main import config


def disable_commands(bot) -> list[str]:
    return [command for command in bot.commands if command not in config["disabled_commands"]]


def splitstring(message, length=2000):
    return [message[i: i + length] for i in range(0, len(message), length)]
