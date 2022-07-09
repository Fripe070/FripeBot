import requests
from discord.ext import commands


class ThatOtherDev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        unfiltered_word_list = requests.get(
            "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
        ).text.split()

        self.word_list = [word for word in unfiltered_word_list if len(word) > 1]

    @commands.command(alliases=["bpcheat"])
    async def bombpartycheat(self, ctx: commands.Context, prompt: str):
        answers = [word for word in self.word_list if prompt.lower() in word.lower()]
        print(answers)
        shortest = ""
        for word in answers:
            if len(word) < len(shortest) or shortest == "":
                shortest = word
        await ctx.reply(shortest)


async def setup(bot):
    await bot.add_cog(ThatOtherDev(bot))
