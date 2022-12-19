import json
import logging
from typing import Any

import discord
from discord.ext import commands

from assets.customfuncs import get_cogs


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.logger = logging.getLogger("discord")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)s %(levelname)s] %(name)s: %(message)s")
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

    # Allows other bots to run commands with my bot, because why not
    async def process_commands(self, message: discord.Message, /) -> None:
        ctx = await self.get_context(message)
        await self.invoke(ctx)


with open("config.json") as f:
    config = json.load(f)

bot = Bot(
    command_prefix=commands.when_mentioned_or(*config["prefixes"]),
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


@bot.tree.context_menu(name="Get Raw Message")
async def raw_msg(interaction: discord.Interaction, message: discord.Message):
    def into_codeblock(text: Any, syntax_highlighting: str = "") -> str:
        return f"```{syntax_highlighting}\n" + str(text).replace("```", "``\u200b`") + "\n```"

    msg = ""
    if message.content:
        msg += f"Content:{into_codeblock(message.content)}"
    if message.embeds:
        msg += f"Embed:{into_codeblock(json.dumps(message.embeds[0].to_dict(), indent=4), 'json')}"

    await interaction.response.send_message(msg, ephemeral=True)


if __name__ == "__main__":
    bot.run(config["token"])
