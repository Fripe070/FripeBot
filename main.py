import discord
import logging
import json

from discord.ext import commands
from assets.customfuncs.get_cogs import get_cogs


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = logging.getLogger("discord")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s %(levelname)s] %(name)s: %(message)s"
        )
        handler = logging.FileHandler("discord.log", "w", "utf-8")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def setup_hook(self):
        bot.logger.info("Loading cogs...")
        for cog in get_cogs("cogs"):
            try:
                await bot.load_extension(cog)
                bot.logger.info(f"Cog loaded: {cog}")
            except Exception as error:
                bot.logger.error(error)


with open("config.json") as f:
    config = json.load(f)

bot = Bot(
    command_prefix=config["prefixes"],
    case_insensitive=True,
    intents=discord.Intents.all(),
    strip_after_prefix=True,
)

for command in bot.commands:
    if command in config["disabled_commands"]:
        command.update(enabled=False)
        bot.logger.info(f'Disabled command: "{command}"')


@bot.event
async def on_ready():
    bot.logger.info(f"Logged in as {bot.user.name} with the id {bot.user.id}")


class Help(commands.HelpCommand):  # TODO Put this in a cog
    def get_command_signature(self, command):
        return command.qualified_name

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"Info about: {self.get_command_signature(command)}"
        )
        if command.help is not None:
            embed.description(value=command.help)
        else:
            embed.description(value="This command doesnt have any further info.")
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", colour=discord.Color.blue())
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(
                    name=cog_name, value=", ".join(command_signatures), inline=False
                )

        channel = self.get_destination()
        await channel.send(embed=embed)


bot.help_command = Help()

if __name__ == "__main__":
    bot.run(config["token"])
