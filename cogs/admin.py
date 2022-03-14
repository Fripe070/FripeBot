import discord
import subprocess
import sys
import os
import asyncio

from discord.ext import commands
from assets.customfuncs.get_cogs import get_cogs
from main import config


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setstatus(self, ctx, activity, *, new_status):
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
            await ctx.reply(f"That's not a valid activity!")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, to_load=None):
        """Loads a specified cog"""
        loads = []
        loadembed = []
        embedcolor = 0x34EB40
        if to_load is None:
            await ctx.reply("Thats not valid.")
            return

        self.bot.logger.info("Loading cogs...")
        for cog in get_cogs(to_load):
            try:
                await self.bot.load_extension(cog)
                self.bot.logger.info(f"Cog loaded: {cog}")
            except Exception as error:
                self.bot.logger.error(error)
                raise error

        print("\n".join(loads))

        embed = discord.Embed(title=f"Loaded cogs!", color=embedcolor, description="‍" + "\n".join(loadembed))
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

        await ctx.message.add_reaction("👍")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, to_unload=None):
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

        print("\n".join(unloads))

        embed = discord.Embed(title=f"Unloaded cogs!", color=embedcolor)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

        await ctx.message.add_reaction("👍")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, to_reload=None):
        """Restarts the bot"""
        reloads = {"successful": [], "errored": []}
        self.bot.logger.info("Loading cogs...")
        for cog in get_cogs(to_reload):
            try:
                await self.bot.load_extension(cog)
                self.bot.logger.info(f"Cog loaded: {cog}")
                reloads["successful"].append(cog)
            except Exception as error:
                self.bot.logger.error(error)
                reloads["errored"].append(cog)

        for command in self.bot.commands:
            if command in config["disabled_commands"]:
                command.update(enabled=False)

        embed = discord.Embed(title=f"Reloaded cogs!", color=0x34EB40)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

        await ctx.message.add_reaction("👍")

    @commands.command(aliases=["die", "shutdown"])
    @commands.is_owner()
    async def stop(self, ctx):
        """Stops the bot"""
        await ctx.message.add_reaction("👍")
        await ctx.reply("Ok. :(\nShutting down...")
        print(f"{ctx.author.name} Told me to stop.")
        self.bot.logger.info(f"{ctx.author.name} Told me to stop.")
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx):
        """Updates the bot"""
        await ctx.message.add_reaction("👍")
        await ctx.reply("Updating...")
        print(f"{ctx.author.name} Told me to update.")
        self.bot.logger.info(f"{ctx.author.name} Told me to update.")
        shellscript = subprocess.Popen(
            ["sh", "update.sh"], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = shellscript.communicate()
        respnse = "Done!"
        if stdout is not None:
            respnse += f"```bash\n{stdout.decode('utf-8')}```"
        if stderr is not None:
            respnse += f"```bash\n{stderr.decode('utf-8')}```"
        await ctx.reply(respnse)


async def setup(bot):
    await bot.add_cog(Admin(bot))
