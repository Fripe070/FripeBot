import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Cog

from main import config


class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        self.bot.logger.error(error)
        if ctx.message.content.lower().startswith(tuple([f"{p}#" for p in config["prefixes"]])):
            return
        # If the command does not exist/is not found.
        if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.DisabledCommand):
            return await ctx.message.add_reaction("❓")
        elif isinstance(error, commands.NotOwner):
            await ctx.message.add_reaction("🔐")
            owner = await self.bot.application_info()
            owner = owner.owner

            def check(reaction, user):
                return user == owner and str(reaction.emoji) == "🔐" and reaction.message == ctx.message

            if await self.bot.wait_for("reaction_add", timeout=60.0, check=check):
                new_ctx = ctx
                # Not really sure why it complains, but it works (I hope)
                # noinspection PyPropertyAccess
                new_ctx.author = owner
                await self.bot.invoke(new_ctx)
            return
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.reply(
                embed=discord.Embed(
                    title="Slow down!",
                    description=f"Try again in {error.retry_after:.2f}s.",
                    color=0xEB4034,
                )
            )
        elif isinstance(error, commands.MemberNotFound) or isinstance(error, commands.UserNotFound):
            return await ctx.reply("That's not a valid user!")
        elif isinstance(error, commands.MessageNotFound):
            return await ctx.send("Did you delete your message? ")
        elif isinstance(error, TimeoutError):
            return
        elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, asyncio.TimeoutError):
            return
        elif (
            isinstance(error, commands.CommandInvokeError)
            and isinstance(error.original, discord.errors.HTTPException)
            and error.original.code == 50035
            and "or fewer in length." in error.original.text
        ):
            return await ctx.send("Too long message.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply(str(error))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)
        else:
            try:
                embed = discord.Embed(
                    title="An error occurred!",
                    description="Please notify the bot owner by "
                    "[making an issue](https://github.com/Fripe070/FripeBot/issues/new) on GitHub.",
                    timestamp=ctx.message.created_at,
                    colour=0xFF0000,
                )
                embed.set_footer(text=f"Caused by {ctx.author} • That's not good!", icon_url=ctx.author.display_avatar)
                embed.add_field(name=type(error).__name__, value=error)

                await ctx.send(embed=embed)
            except Exception as e:
                self.bot.logger.error(e)
            raise error


async def setup(bot):
    await bot.add_cog(Error(bot))
