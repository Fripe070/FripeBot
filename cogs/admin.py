from assets.stuff import *


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @bot.command(help="Sets the bots status")
        async def setstatus(ctx, activity, *, new_status):
            if ctx.author.id in trusted:
                status = new_status
                if activity == "watching":
                    print(f'{bcolors.BOLD + bcolors.OKBLUE}Status set to "{bcolors.OKCYAN}{activity} {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
                    await bot.change_presence(
                        activity=discord.Activity(name=status, type=discord.ActivityType.watching))
                    await ctx.reply(f'Status set to "{activity} {status}"')

                elif activity == "playing":
                    print(f'{bcolors.BOLD + bcolors.OKBLUE}Status set to "{bcolors.OKCYAN}{activity} {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
                    await bot.change_presence(
                        activity=discord.Activity(name=status, type=discord.ActivityType.playing))
                    await ctx.reply(f'Status set to "{activity} {status}"')

                elif activity == "listening":
                    print(f'{bcolors.BOLD + bcolors.OKBLUE}Status set to "{bcolors.OKCYAN}{activity} {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
                    await bot.change_presence(
                        activity=discord.Activity(name=status, type=discord.ActivityType.listening))
                    await ctx.reply(f'Status set to "{activity} to {status}"')

                elif activity == "competing":
                    print(f'{bcolors.BOLD + bcolors.OKBLUE}Status set to "{bcolors.OKCYAN}{activity} {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
                    await bot.change_presence(
                        activity=discord.Activity(name=status, type=discord.ActivityType.competing))
                    await ctx.reply(f'Status set to "{activity} in {status}"')
                else:
                    await ctx.reply(f"That's not a valid activity!")

            else:
                print(f'{bcolors.FAIL}{ctx.author.name}{bcolors.WARNING} Tried to change the status to "{bcolors.FAIL}{activity} {new_status}{bcolors.WARNING}"{bcolors.ENDC}')
                await ctx.message.add_reaction("🔐")

        @bot.command(help="Restarts the bot")  # Currently not working
        async def reload(ctx, to_reload=None):
            if ctx.author.id in trusted:
                reloads = []
                reloadembed = []
                await ctx.message.add_reaction("👍")
                print(f"{bcolors.OKBLUE}Reloading cogs!{bcolors.ENDC}")
                embedcolor = 0x34eb40
                for cog in os.listdir("COGS"):
                    if cog.endswith(".py"):
                        try:
                            bot.reload_extension(f"cogs.{cog[:-3]}")
                            reloads.append(f"{bcolors.OKBLUE}│ {bcolors.OKGREEN}{cog}{bcolors.ENDC}")
                            reloadembed.append(f"<:Check:829656697835749377> {cog}")
                        except:
                            reloads.append(f"{bcolors.FAIL}│ {bcolors.WARNING}{cog}{bcolors.ENDC}")
                            reloadembed.append(f"<:warning:829656327797604372> {cog}")
                            embedcolor = 0xeb4034
                print("\n".join(reloads))

                embed = discord.Embed(title=f"Reloaded cogs!", color=embedcolor, description="‍"+"\n".join(reloadembed))
                embed.set_footer(text=f"Requested by {ctx.author}")
                await ctx.send(embed=embed)
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