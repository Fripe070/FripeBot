from assets.stuff import *


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @bot.command(help="Gives soup")
        async def soup(ctx):
            await ctx.reply("Here's your soup! <:soup:823158453022228520>")

        @bot.command(aliases=['flip'], help="Flips a coin!")
        async def coinflip(ctx):
            await ctx.reply(random.choice(["Heads!", "Tails!"]))

        @bot.command(aliases=['8ball'], help="A magic eightball")
        async def eightball(ctx):
            await ctx.reply(
                random.choice(["Yes", "No", "<:perhaps:819028239275655169>", "Surely", "Maybe tomorrow", "Not yet"]))

        @bot.command(help="Kill someone with a randomized Minecraft death message")
        async def kill(ctx, person1 = None):
            if person1 == "None":
                await ctx.reply("You need to specify who to kill!")
            temp_message = random.choice(list(death_messages.values()))
            temp_message = temp_message.replace("person1", str(person1))
            temp_message = temp_message.replace("person2", str(ctx.author.mention))
            temp_message = temp_message.replace("itemhere", random.choice(list(mcitems.values())))
            await ctx.message.delete()
            await ctx.send(temp_message)

        @bot.command(aliases=["ikill"], help="Kill someone with a randomized Minecraft death message")
        async def itemkill(ctx, person1 = None):
            if person1 == "None":
                await ctx.reply("You need to specify who to kill!")
            else:
                temp_message = random.choice(list(item_deaths.values()))
                temp_message = temp_message.replace("person1", str(person1))
                temp_message = temp_message.replace("person2", str(ctx.author.mention))
                temp_message = temp_message.replace("itemhere", random.choice(list(mcitems.values())))
                await ctx.message.delete()
                await ctx.send(temp_message)

        @bot.command(aliases=['Say'], help="Makes the bot say things")
        async def echo(ctx, *, tell):
            if ctx.author.id in trusted:
                if isinstance(ctx.channel, discord.channel.DMChannel):
                    print(f'{bcolors.BOLD + bcolors.WARNING}{ctx.author}{bcolors.ENDC + bcolors.FAIL} Tried to make me say: "{bcolors.WARNING + bcolors.BOLD}{tell}{bcolors.ENDC + bcolors.FAIL}" In a dm{bcolors.ENDC}')
                    await ctx.send("That command isn't available in dms")
                else:
                    print(f'{bcolors.BOLDOKCYAN}{ctx.author}{bcolors.ENDC} Made me say: "{bcolors.OKBLUE + bcolors.BOLD}{tell}{bcolors.ENDC}"')
                    await ctx.message.delete()
                    await ctx.send(tell)
            else:
                print(f'{bcolors.BOLDWARN}{ctx.author}{bcolors.ENDC}{bcolors.FAIL} Tried to make me say: "{bcolors.WARNING}{tell}{bcolors.ENDC}{bcolors.FAIL}" But '"wasnt"f' allowed to{bcolors.ENDC}')
                await ctx.message.add_reaction("🔐")

def setup(bot):
    bot.add_cog(Fun(bot))
