"""from discord.ext import commands
from assets.stuff import *


with open("../config.json") as f:
    config = json.load(f)

prefix = config["prefixes"]
trusted = config["trusted"]


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @Cog.listener()
        async def on_ready(self):
            if not self.bot.ready:
                self.bot.cogs_ready.ready_up("utility")

        @bot.command(help="Sets the bots status")
        async def setstatus(ctx, activity, *,
                            new_status):  # need to make ppl able to set the status to gaming/watching etc
            if ctx.author.id in trusted:
                status = new_status

                if activity == "watching":
                    print(
                        f'{bcolors.BOLD + bcolors.OKBLUE}Status set to "{bcolors.OKCYAN}{activity} {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
                    await bot.change_presence(
                        activity=discord.Activity(name=status, type=discord.ActivityType.watching))
                    await ctx.reply(f'Status set to "{activity} {status}"')

                elif activity == "playing":
                    print(
                        f'{bcolors.BOLD + bcolors.OKBLUE}Status set to "{bcolors.OKCYAN}{activity} {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
                    await bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.playing))
                    await ctx.reply(f'Status set to "{activity} {status}"')

                elif activity == "listening":
                    print(
                        f'{bcolors.BOLD + bcolors.OKBLUE}Status set to "{bcolors.OKCYAN}{activity} {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
                    await bot.change_presence(
                        activity=discord.Activity(name=status, type=discord.ActivityType.listening))
                    await ctx.reply(f'Status set to "{activity} to {status}"')
                else:
                    await ctx.reply(f"That's not a valid activity!")

            else:
                print(
                    f'{bcolors.FAIL}{ctx.author.name}{bcolors.WARNING} Tried to change the status to "{bcolors.FAIL}{activity} {new_status}{bcolors.WARNING}"{bcolors.ENDC}')
                await ctx.message.add_reaction("🔐")

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



def setup(bot):
    bot.add_cog(Admin(bot))"""