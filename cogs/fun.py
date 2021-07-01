from assets.stuff import *


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(help="Gives soup")
    async def soup(self, ctx):
        await ctx.reply("Here's your soup! <:soup:823158453022228520>")

    @command(aliases=['flip'], help="Flips a coin!")
    async def coinflip(self, ctx):
        await ctx.reply(random.choice(["Heads!", "Tails!"]) + ":coin:")

    @command(help="Rolls a dice!")
    async def dice(self, ctx, sides = 6):
        await ctx.reply(f"You rolled a {random.randint(1, sides)}! :game_die:")

    @command(aliases=['8ball'], help="A magic eightball")
    async def eightball(self, ctx):
        await ctx.reply(
            random.choice(["Yes", "No", "<:perhaps:819028239275655169>", "Surely", "Maybe tomorrow", "Not yet"]))

    @command()
    async def jumbo(self, ctx, jumbo):
        if jumbo.startswith("<a:"):
            temp = "gif"
        else:
            temp = "png"
        print(jumbo)
        await ctx.reply(f"https://cdn.discordapp.com/emojis/{jumbo.split(':')[2][:-1]}.{temp}")

    @command(help="Kill someone with a randomized Minecraft death message")
    async def kill(self, ctx, person1 = None):
        if person1 is None:
            person1 = random.choice(list(entites.values()))
        if "panda" in person1:
            await ctx.reply("How dare you try to kill a panda >:(")
        else:
            temp_message = random.choice(list(death_messages.values()))
            temp_message = temp_message.replace("%1$s", str(person1))
            temp_message = temp_message.replace("%2$s", str(ctx.author.mention))
            temp_message = temp_message.replace("%3$s", random.choice(list(mcitems.values())))
            await ctx.message.delete()
            await ctx.send(temp_message)

    @command(aliases=["ikill"], help="Kill someone with a randomized Minecraft death message")
    async def itemkill(self, ctx, person1 = None):
        if person1 is None:
            person1 = random.choice(list(entites.values()))
        if "panda" in person1:
            await ctx.reply("How dare you try to kill a panda >:(")
        else:
            temp_message = random.choice(list(item_deaths.values()))
            temp_message = temp_message.replace("%1$s", str(person1))
            temp_message = temp_message.replace("%2$s", str(ctx.author.mention))
            temp_message = temp_message.replace("%3$s", random.choice(list(mcitems.values())))
            await ctx.message.delete()
            await ctx.send(temp_message)

    @command(aliases=['Say'], help="Makes the bot say things")
    async def echo(self, ctx, *, tell):
        if ctx.author.id in trusted:
            if isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.send("That command isn't available in dms")
            else:
                await ctx.message.delete()
                await ctx.send(tell)
        else:
            await ctx.message.add_reaction("🔐")

    @command(aliases=['esay'], help="Makes the bot say things")
    async def embedecho(self, ctx, *, tell):
        if ctx.author.id in trusted:
            if isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.send("That command isn't available in dms")
            else:
                await ctx.message.delete()
                embed = discord.Embed(title="This is a embed! :o",
                                      description=tell)
                embed.set_footer(text=f"Requested by {ctx.author}")
                await ctx.send(embed=embed)
        else:
            await ctx.message.add_reaction("🔐")


def setup(bot):
    bot.add_cog(Fun(bot))
