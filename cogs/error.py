import asyncio
import contextlib

import discord
from discord.ext import commands

from main import config


class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        self.bot.logger.error(error)
        if ctx.message.content.lower().startswith(tuple(f"{p}#" for p in config["prefixes"])):
            return

        if isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, (asyncio.TimeoutError, TimeoutError)):
                return
            elif (
                isinstance(error.original, discord.errors.HTTPException)
                and error.original.code == 50035
                and "or fewer in length." in error.original.text
            ):
                return await ctx.send("Too long message.")

        # If the command does not exist/is not found.
        if isinstance(error, (commands.CommandNotFound, commands.DisabledCommand)):
            return await ctx.message.add_reaction("❓")
        elif isinstance(error, commands.NotOwner):
            await ctx.message.add_reaction("🔐")
            owner = await self.bot.application_info()
            owner = owner.owner

            def check(reaction, user):
                return user == owner and str(reaction.emoji) == "🔐" and reaction.message == ctx.message

            with contextlib.suppress(asyncio.exceptions.TimeoutError):
                if await self.bot.wait_for("reaction_add", timeout=120.0, check=check):
                    new_ctx = ctx
                    # Replaces the ctx message author with the bot owner, thus allowing the command to execute
                    new_ctx.__setattr__("author", owner)

                    with contextlib.suppress(discord.Forbidden):
                        await ctx.message.clear_reaction("🔐")
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
        elif isinstance(error, (commands.MemberNotFound, commands.UserNotFound)):
            return await ctx.reply("That's not a valid user!")
        elif isinstance(error, commands.MessageNotFound):
            return await ctx.send("Did you delete your message? ")
        elif isinstance(error, TimeoutError):
            return
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.reply(str(error))
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send_help(ctx.command)
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


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Error(bot))
