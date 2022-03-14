import discord
import asyncio

from discord.ext import commands
from discord.ext.commands import Cog
from assets.stuff import col


class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        # If the command does not exist/is not found.
        if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.DisabledCommand):
            await ctx.message.add_reaction("❓")
        elif isinstance(error, commands.NotOwner):
            await ctx.message.add_reaction("🔐")
            owner = await self.bot.application_info()
            owner = owner.owner

            def check(reaction, user):
                return user == owner and str(reaction.emoji) == "🔐" and reaction.message == ctx.message

            if await self.bot.wait_for("reaction_add", timeout=60.0, check=check):
                new_ctx = ctx
                new_ctx.author = owner
                await self.bot.invoke(new_ctx)

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                embed=discord.Embed(
                    title=f"Slow down!", description=f"Try again in {error.retry_after:.2f}s.", color=0xEB4034
                )
            )
        elif isinstance(error, commands.MemberNotFound) or isinstance(error, commands.UserNotFound):
            await ctx.reply("That's not a valid user!")
        elif isinstance(error, commands.MessageNotFound):
            await ctx.send("Did you delete your message? ")
        elif isinstance(error, TimeoutError):
            pass
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply(error)
        elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, asyncio.TimeoutError):
            return
        else:
            try:
                embed = discord.Embed(
                    title="An error occurred! Please notify Fripe if necessary.",
                    description=f"```{error}```",
                    timestamp=ctx.message.created_at,
                    colour=0xFF0000,
                )
                embed.set_footer(text=f"Caused by {ctx.author}")
                await ctx.send(embed=embed)
            except Exception:
                print(f"{col.WARN + col.BOLD}Failed to send chat message{col.ENDC}")
            raise error


async def setup(bot):
    await bot.add_cog(Error(bot))
