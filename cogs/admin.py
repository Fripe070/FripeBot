import discord
import subprocess
import sys
import os
import asyncio

from discord.ext import commands
from assets.stuff import col, getcogs


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setstatus(self, ctx, activity, *, new_status):
        """Sets the bots status"""
        status = new_status
        if activity == "watching":
            print(f'{col.BLUE}{col.BOLD}Status set to "{col.CYAN}{activity} {status}{col.BLUE}"{col.ENDC}')
            await self.bot.change_presence(
                activity=discord.Activity(name=status, type=discord.ActivityType.watching))
            await ctx.reply(f'Status set to "{activity} {status}"')

        elif activity == "playing":
            print(f'{col.BLUE}{col.BOLD}Status set to "{col.CYAN}{activity} {status}{col.BLUE}"{col.ENDC}')
            await self.bot.change_presence(
                activity=discord.Activity(name=status, type=discord.ActivityType.playing))
            await ctx.reply(f'Status set to "{activity} {status}"')

        elif activity == "listening":
            print(f'{col.BLUE}{col.BOLD}Status set to "{col.CYAN}{activity} {status}{col.BLUE}"{col.ENDC}')
            await self.bot.change_presence(
                activity=discord.Activity(name=status, type=discord.ActivityType.listening))
            await ctx.reply(f'Status set to "{activity} to {status}"')

        elif activity == "competing":
            print(f'{col.BLUE}{col.BOLD}Status set to "{col.CYAN}{activity} in {status}{col.BLUE}"{col.ENDC}')
            await self.bot.change_presence(
                activity=discord.Activity(name=status, type=discord.ActivityType.competing))
            await ctx.reply(f'Status set to "{activity} in {status}"')
        else:
            await ctx.reply(f"That's not a valid activity!")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, to_load=None):
        """Loads a specified cog"""
        loads = []
        loadembed = []
        embedcolor = 0x34eb40
        if to_load is None:
            await ctx.reply("Thats not valid.")
            return
        else:
            print(f"{col.BLUE}Loading cog(s)!{col.ENDC}")
        for cog in getcogs(to_load):
            try:
                self.bot.load_extension(f"{cog}")
                loads.append(f"{col.BLUE}│ {col.GREEN}{cog}")
                loadembed.append(f"<:Check:829656697835749377> {cog}")
            except Exception as error:
                loads.append(f"{col.FAIL}│ {col.WARN}{error}")
                loadembed.append(f"<:warning:829656327797604372> {error}")
                embedcolor = 0xeb4034

        print("\n".join(loads))

        embed = discord.Embed(title=f"Loaded cogs!", color=embedcolor,
                              description="‍" + "\n".join(loadembed))
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

        await ctx.message.add_reaction("👍")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, to_unload=None):
        """Unloads a specified cog"""
        unloads = []
        unloadembed = []
        embedcolor = 0x34eb40
        if to_unload is None:
            await ctx.reply("Thats not valid.")
            return
        else:
            print(f"{col.BLUE}Unloading cog(s)!{col.ENDC}")
        for cog in getcogs(to_unload):
            try:
                self.bot.unload_extension(f"{cog}")
                unloads.append(f"{col.BLUE}│ {col.GREEN}{cog}")
                unloadembed.append(f"<:Check:829656697835749377> {cog}")
            except Exception as error:
                unloads.append(f"{col.FAIL}│ {col.WARN}{error}")
                unloadembed.append(f"<:warning:829656327797604372> {error}")
                embedcolor = 0xeb4034

        print("\n".join(unloads))

        embed = discord.Embed(title=f"Unloaded cogs!", color=embedcolor,
                              description="‍" + "\n".join(unloadembed))
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

        await ctx.message.add_reaction("👍")

    @commands.command()  # Currently not working
    @commands.is_owner()
    async def reload(self, ctx, to_reload=None):
        """Restarts the bot"""
        reloads = []
        reloadembed = []
        embedcolor = 0x34eb40
        if getcogs(to_reload) is None:
            await ctx.reply("Thats not valid.")
            return
        else:
            print(f"{col.BLUE}Reloading cog(s)!{col.ENDC}")
        for cog in getcogs(to_reload):
            try:
                self.bot.reload_extension(f"{cog}")
                reloads.append(f"{col.BLUE}│ {col.GREEN}{cog}")
                reloadembed.append(f"<:Check:829656697835749377> {cog}")
            except Exception as error:
                reloads.append(f"{col.FAIL}│ {col.WARN}{error}")
                reloadembed.append(f"<:warning:829656327797604372> {error}")
                embedcolor = 0xeb4034

        print("\n".join(reloads))

        embed = discord.Embed(title=f"Reloaded cogs!", color=embedcolor,
                              description="‍" + "\n".join(reloadembed))
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

        await ctx.message.add_reaction("👍")

    @commands.command(aliases=['die', 'shutdown'])
    @commands.is_owner()
    async def stop(self, ctx):
        """Stops the bot"""
        await ctx.message.add_reaction("👍")
        await ctx.reply("Ok. :(\nshutting down...")
        print(f"{col.FAIL}{col.BOLD}{ctx.author.name} Told me to stop{col.ENDC}")
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx):
        """Updates the bot"""
        await ctx.message.add_reaction("👍")
        await ctx.reply("Updating...")
        print(f"{col.FAIL}{col.BOLD}{ctx.author.name} Told me to update{col.ENDC}")
        shellscript = subprocess.Popen(
            ["update.sh"],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = shellscript.communicate()
        respnse = "Done!"
        if stdout is not None:
            respnse += f"```bash\n{stdout.decode('utf-8')}```"
        if stderr is not None:
            respnse += f"```bash\n{stderr.decode('utf-8')}```"
        await ctx.reply(respnse)
        os.execv(sys.executable, ['python3'] + sys.argv)


def setup(bot):
    bot.add_cog(Admin(bot))
