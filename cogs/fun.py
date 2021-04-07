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


def setup(bot):
    bot.add_cog(Fun(bot))