import discord
import re

from discord.ext import commands
from discord.ext.commands import *


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message):
        if message.author != self.bot.user:
            # Detect if the bot is mentioned in the message
            if f"<@{self.bot.user.id}>" in message.content or f"<@!{self.bot.user.id}>" in message.content:
                await message.add_reaction("<:ping_gun:823948139504861225>")
                await message.reply("My prefix is `f!`", delete_after=5, mention_author=False)

            if message.channel.type == discord.ChannelType.private:
                channel = self.bot.get_channel(920014770206294129)
                if message.attachments:
                    files = []
                    for file in message.attachments:
                        files.append(await file.to_file())
                else:
                    files = None
                await channel.send(f"{message.content}", files=files)

            if message.content == "🤡":
                await message.reply(
                    "https://cdn.discordapp.com/attachments/776166607448965133/862286194422710272/argument.mp4"
                )

    @Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        rgbs = re.findall(r"#[0-9A-Fa-f]{6}", message.content)
        for rgb in rgbs:
            await message.reply(f"", mention_author=False)


async def setup(bot):
    await bot.add_cog(Listeners(bot))
