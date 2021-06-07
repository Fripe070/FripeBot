from assets.stuff import *


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(help="Sets the bots status")
    async def setstatus(self, ctx, activity, *, new_status):
        if ctx.author.id in trusted:
            status = new_status
            if activity == "watching":
                print(f'{bcolors.BOLDOKBLUE}Status set to "{bcolors.OKCYAN}{activity} {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
                await bot.change_presence(
                    activity=discord.Activity(name=status, type=discord.ActivityType.watching))
                await ctx.reply(f'Status set to "{activity} {status}"')

            elif activity == "playing":
                print(f'{bcolors.BOLDOKBLUE}Status set to "{bcolors.OKCYAN}{activity} {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
                await bot.change_presence(
                    activity=discord.Activity(name=status, type=discord.ActivityType.playing))
                await ctx.reply(f'Status set to "{activity} {status}"')

            elif activity == "listening":
                print(f'{bcolors.BOLDOKBLUE}Status set to "{bcolors.OKCYAN}{activity} {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
                await bot.change_presence(
                    activity=discord.Activity(name=status, type=discord.ActivityType.listening))
                await ctx.reply(f'Status set to "{activity} to {status}"')

            elif activity == "competing":
                print(f'{bcolors.BOLDOKBLUE}Status set to "{bcolors.OKCYAN}{activity} in {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
                await bot.change_presence(
                    activity=discord.Activity(name=status, type=discord.ActivityType.competing))
                await ctx.reply(f'Status set to "{activity} in {status}"')
            else:
                await ctx.reply(f"That's not a valid activity!")

        else:
            print(f'{bcolors.FAIL}{ctx.author.name}{bcolors.WARNING} Tried to change the status to "{bcolors.FAIL}{activity} {new_status}{bcolors.WARNING}"{bcolors.ENDC}')
            await ctx.message.add_reaction("🔐")

    @command(help="Restarts the bot")  # Currently not working
    async def reload(self, ctx, to_reload=None):
        if ctx.author.id in trusted:
            reloads = []
            reloadembed = []
            embedcolor = 0x34eb40
            if getcogs(to_reload) is None:
                await ctx.reply("Thats not valid.")
                return
            else:
                print(f"{bcolors.OKBLUE}Reloading cog(s)!{bcolors.ENDC}")
            for cog in getcogs(to_reload):
                try:
                    bot.reload_extension(f"{cog}")
                    reloads.append(f"{bcolors.OKBLUE}│ {bcolors.OKGREEN}{cog}")
                    reloadembed.append(f"<:Check:829656697835749377> {cog}")
                except Exception as error:
                    reloads.append(f"{bcolors.FAIL}│ {bcolors.WARNING}{error}")
                    reloadembed.append(f"<:warning:829656327797604372> {error}")
                    embedcolor = 0xeb4034

            print("\n".join(reloads))

            embed = discord.Embed(title=f"Reloaded cogs!", color=embedcolor,
                                  description="‍" + "\n".join(reloadembed))
            embed.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=embed)

            await ctx.message.add_reaction("👍")
        else:
            await ctx.message.add_reaction("🔐")

    @command(aliases=['die'], help="Stops the bot")
    async def stop(self, ctx):
        if ctx.author.id in trusted:
            await ctx.message.add_reaction("👍")
            await ctx.reply("Ok. :(")
            print(f"{bcolors.BOLDFAIL}{ctx.author.name} Told me to stop{bcolors.ENDC}")
            await bot.logout()
            await bot.close()
        else:
            await ctx.message.add_reaction("🔐")


def setup(bot):
    bot.add_cog(Admin(bot))
