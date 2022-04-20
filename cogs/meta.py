import discord
import sys

from discord.ext import commands


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["source", "git"], help="Links my GitHub profile")
    async def github(self, ctx: commands.Context, user: discord.User = None):
        """Links the bots GitHub repository"""
        await ctx.message.delete()
        embed = discord.Embed(
            title="FripeBot",
            description="This bot is open source!",
            url="https://github.com/Fripe070/FripeBot",
            color=ctx.author.color,
            timestamp=ctx.message.created_at,
        )
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/72686066")
        embed.set_footer(text=f"Requested by: {ctx.author.display_name}", icon_url=ctx.author.avatar)
        if user is None:
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{user.mention} Please take a look at my github", embed=embed)

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Displays the bots ping"""
        await ctx.message.add_reaction("🏓")
        bot_ping = round(self.bot.latency * 1000)
        if bot_ping < 130:
            color = 0x44FF44
        elif 130 < bot_ping < 180:
            color = 0xFF8C00
        else:
            color = 0xFF2200
        embed = discord.Embed(
            title="Pong! :ping_pong:",
            description=f"The ping is **{bot_ping}ms!**",
            color=color,
        )
        await ctx.reply(embed=embed)

    @commands.command(alias=["botstatus", "botinfo"])
    async def status(self, ctx: commands.Context):
        """Displays various statistics about the bot."""
        embed = discord.Embed(
            title="Bot status",
            colour=ctx.author.colour,
            timestamp=ctx.message.created_at,
        )

        pyver = sys.version_info

        embed.description = f"""
Python Version: {pyver.major}.{pyver.minor}.{pyver.micro}
Pycord Version: {discord.__version__}"""
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Meta(bot))
