import asyncio
import contextlib
import re

import discord
from discord.ext import commands

from main import config


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        # Detect if the bot is mentioned in the message
        if f"<@{self.bot.user.id}>" in message.content or f"<@!{self.bot.user.id}>" in message.content:
            await message.add_reaction("<:ping_gun:823948139504861225>")

        if message.channel.type == discord.ChannelType.private:
            channel = self.bot.get_channel(920014770206294129)
            if message.attachments:
                files = [await file.to_file() for file in message.attachments]
            else:
                files = None
            await channel.send(f"{message.content}", files=files)

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) == "🚮" and reaction.message == msg

        if message.content == "🤡":
            msg = await message.reply(
                "https://cdn.discordapp.com/attachments/776166607448965133/862286194422710272/argument.mp4"
            )
            await msg.add_reaction("🚮")
            with contextlib.suppress(asyncio.exceptions.TimeoutError):
                await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                await msg.delete()

        prefixes = config["prefixes"]  # doesn't work when I put this directly inside the regex
        # noinspection RegExpUnnecessaryNonCapturingGroup
        if colours := re.findall(rf"(?:{'|'.join(prefixes)})#([\dA-Fa-f]{{6}})", message.content, flags=re.IGNORECASE):
            for colour in colours:
                url = f"https://www.colorhexa.com/{colour}.png"

                await message.reply(url, mention_author=False)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent):
        try:
            message = await self.bot.get_channel(reaction.channel_id).fetch_message(reaction.message_id)
        except discord.errors.NotFound:
            return

        if message.author == self.bot.user:
            return

        trash_reaction: discord.reaction.Reaction = next(
            (msg_reaction for msg_reaction in message.reactions if msg_reaction.emoji == "🚮"), None
        )
        if trash_reaction is None:
            return

        if trash_reaction.count - trash_reaction.me >= 2:
            # Message is already deleted
            with contextlib.suppress(discord.HTTPException):
                await message.delete()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Listeners(bot))
