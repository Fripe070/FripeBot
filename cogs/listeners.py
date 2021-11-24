import discord
from discord.ext import commands
from discord.ext.commands import *
from assets.stuff import col


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message):
        if message.author != self.bot.user:
            # Detect if the bot is pinged in the message
            if f"<@{self.bot.user.id}>" in message.content or f"<@!{self.bot.user.id}>" in message.content:
                await message.add_reaction("<:ping_gun:823948139504861225>")
                await message.reply("My prefix is `f!`", delete_after=5)

            if isinstance(message.channel, discord.channel.DMChannel):  # If message was send in a dm
                print(f"{message.author} Send this in a DM: {message.content}")

            if message.content == "🤡":
                await message.reply("https://cdn.discordapp.com/attachments/776166607448965133/862286194422710272/argument.mp4")

    @Cog.listener()
    async def on_command_completion(self, ctx):
        print(f"Command was executed by {col.CYAN}{ctx.message.author}\n{col.HEADER}{ctx.message.content}{col.ENDC}")


def setup(bot):
    bot.add_cog(Listeners(bot))
