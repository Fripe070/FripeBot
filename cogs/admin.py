from assets.stuff import *


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @commands.command(help="Sets the bots status")
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
                print(f'{bcolors.FAIL}{ctx.author.name}{bcolors.WARNING} Tried to change the status to "{bcolors.FAIL}{activity} {new_status}{bcolors.WARNING}"{bcolors.ENDC}')
                await ctx.message.add_reaction("🔐")

        @bot.command(help="Restarts the bot")  # Currently not working
        async def reload(ctx):
            if ctx.author.id in trusted:
                reloads = []
                failedreloads = []
                successfulreloads = []
                await ctx.message.add_reaction("👍")
                print(f"{bcolors.OKBLUE}Reloading cogs!{bcolors.ENDC}")
                for cog in COGS:
                    try:
                        bot.reload_extension(f"cogs.{cog}")
                        reloads.append(f"{bcolors.OKBLUE}│ {bcolors.OKGREEN}{cog}{bcolors.ENDC}")
                        successfulreloads.append(cog)
                    except:
                        reloads.append(f"{bcolors.FAIL}│ {bcolors.WARNING}{cog}{bcolors.ENDC}")
                        failedreloads.append(cog)
                print("\n".join(reloads))
                embed = discord.Embed(title=f"Reloaded cogs!", color=0xeb4034)
                embed.set_footer(text=f"Requested by {ctx.author}")
                await ctx.send("Successful reloads:```\n" + "\n".join(successfulreloads) + "```Failed reloads:```" + "\n".join(failedreloads) + "```")
            else:
                await ctx.message.add_reaction("🔐")

        @bot.command(aliases=['die', 'kill'], help="Stops the bot")
        async def stop(ctx):
            if ctx.author.id in trusted:
                await ctx.message.add_reaction("👍")
                await ctx.reply("Ok. :(")
                print(f"{bcolors.FAIL + bcolors.BOLD}{ctx.author.name} Told me to stop{bcolors.ENDC}")
                await bot.logout()
                await bot.close()
            else:
                await ctx.message.add_reaction("🔐")


def setup(bot):
    bot.add_cog(Admin(bot))