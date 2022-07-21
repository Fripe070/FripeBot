import asyncio
import subprocess

import discord
from discord.ext import commands

from assets.customfuncs.get_cogs import get_cogs
from main import config


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def setstatus(self, ctx: commands.Context, activity, *, new_status=None):
        """Sets the bots status"""
        status = new_status

        if activity == "watching":
            self.bot.logger.info(f'Status set to "{activity} {status}')
            await self.bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.watching))
            await ctx.reply(f'Status set to "{activity} {status}"')

        elif activity == "playing":
            self.bot.logger.info(f'Status set to "{activity} {status}')
            await self.bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.playing))
            await ctx.reply(f'Status set to "{activity} {status}"')

        elif activity == "listening":
            self.bot.logger.info(f'Status set to "{activity} to {status}')
            await self.bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.listening))
            await ctx.reply(f'Status set to "{activity} to {status}"')

        elif activity == "competing":
            self.bot.logger.info(f'Status set to "{activity} in {status}')
            await self.bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.competing))
            await ctx.reply(f'Status set to "{activity} in {status}"')
        else:
            await ctx.reply("That's not a valid activity!")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: commands.Context, to_load=None):
        """Loads a specified cog"""
        if to_load is None:
            await ctx.reply("Thats not a valid cog.")
            return

        embed_color = discord.Color.green()
        embed_desc = ""

        self.bot.logger.info("Loading cogs...")
        for cog in get_cogs(to_load):
            try:
                await self.bot.load_extension(cog)
                self.bot.logger.info(f"Cog loaded: {cog}")
                embed_desc += f"<:RedX:999549005342187620> {cog}\n"
            except Exception as error:
                self.bot.logger.error(error)
                embed_color = discord.Color.red()
                embed_desc += f"✅ {cog} - {error}\n"
                raise error

        embed = discord.Embed(title="Loaded cog(s)!", description=embed_desc, color=embed_color)

        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

        await ctx.message.add_reaction("👍")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, to_unload=None):
        """Unloads a specified cog"""
        unloads = {"successful": [], "errored": []}
        embedcolor = 0x34EB40
        if to_unload is None:
            await ctx.reply("Thats not valid.")
            return

        self.bot.logger.info("Unloading cogs...")
        for cog in get_cogs(to_unload):
            try:
                await self.bot.unload_extension(cog)
                self.bot.logger.info(f"Cog loaded: {cog}")
                unloads["successful"].append(cog)
            except Exception as error:
                self.bot.logger.error(error)
                unloads["errored"].append(cog)

        embed = discord.Embed(title="Unloaded cogs!", color=embedcolor)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

        await ctx.message.add_reaction("👍")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, to_reload="cogs"):
        """Restarts the bot"""

        embed_color = discord.Color.green()
        embed_desc = ""

        self.bot.logger.info("Reloading cogs...")
        for cog in get_cogs(to_reload):
            try:
                await self.bot.reload_extension(cog)
                self.bot.logger.info(f"Cog reloaded: {cog}")
                embed_desc += f"✅ {cog}\n"
            except Exception as error:
                self.bot.logger.error(error)
                embed_color = discord.Color.red()
                embed_desc += f"<:RedX:999549005342187620> {cog} - {error}\n"

        for command in self.bot.commands:
            if command in config["disabled_commands"]:
                command.update(enabled=False)

        embed = discord.Embed(title="Reloaded cog(s)!", description=embed_desc, color=embed_color)

        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

        await ctx.message.add_reaction("👍")

    @commands.command(aliases=["die", "shutdown"])
    @commands.is_owner()
    async def stop(self, ctx: commands.Context):
        """Stops the bot"""
        await ctx.message.add_reaction("👍")
        await ctx.reply("Ok. :(\nShutting down...")
        self.bot.logger.info(f"{ctx.author.name} Told me to shut down.")
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx: commands.Context):
        """Updates the bot"""
        await ctx.message.add_reaction("👍")
        await ctx.reply("Updating...")
        self.bot.logger.info(f"{ctx.author.name} Told me to update.")
        shellscript = subprocess.Popen(
            ["sh", "update.sh"],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = shellscript.communicate()
        respnse = "Done!"
        if stdout is not None:
            respnse += f"```bash\n{stdout.decode('utf-8')}```"
        if stderr is not None:
            respnse += f"```bash\n{stderr.decode('utf-8')}```"
        await ctx.reply(respnse)


async def setup(bot):
    await bot.add_cog(Owner(bot))
