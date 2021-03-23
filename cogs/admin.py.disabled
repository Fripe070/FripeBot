import discord
from discord.ext import commands
from discord.ext.commands import *
import json


with open("../config.json") as f:
    config = json.load(f)

prefix = config["prefixes"]
trusted = config["trusted"]


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @commands.command(help="Restarts the bot")  # Currently not working
        async def restart(ctx):
            if ctx.author.id in trusted:
                await ctx.message.add_reaction("👍")
                await ctx.reply("Restarting! :D")
                bot.reload_extension('main')
            else:
                await ctx.message.add_reaction("🔐")

        @commands.command(aliases=['die', 'kill'], help="Stops the bot")
        async def stop(ctx):
            if ctx.author.id in trusted:
                await ctx.message.add_reaction("👍")
                await ctx.reply("Ok. :(")
                print(f"{bcolors.FAIL + bcolors.BOLD}{ctx.author.name} Told me to stop{bcolors.ENDC}")
                await bot.close()
            else:
                await ctx.message.add_reaction("🔐")

        @Cog.listener()
        async def on_ready(self):
            if not self.bot.ready:
                self.bot.cogs_ready.ready_up("utility")

def setup(bot):
    bot.add_cog(Admin(bot))