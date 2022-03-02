import discord
import random

from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Gives soup")
    async def soup(self, ctx):
        await ctx.reply("Here's your soup! <:soup:823158453022228520>")

    @commands.command(aliases=['flip'], help="Flips a coin!")
    async def coinflip(self, ctx):
        await ctx.reply(random.choice(["Heads!", "Tails!"]) + ":coin:")

    @commands.command(help="Rolls a dice!")
    async def dice(self, ctx, sides=6):
        await ctx.reply(f"You rolled a {random.randint(1, sides)}! :game_die:")

    @commands.command(aliases=['8ball'], help="A magic eightball")
    async def eightball(self, ctx):
        await ctx.reply(random.choice([
            "Yes",
            "No",
            "<:perhaps:819028239275655169>",
            "Surely",
            "Maybe tomorrow",
            "Not yet",
            "If you say so 🙃",
            "Absolutely!",
            "For sure!",
            "I don't think so",
            "I don't know",
            "If you want it to be 😉"
        ]))

    @commands.command(help="Scrambles the text supplied")
    async def scramble(self, ctx, *, arg):
        await ctx.reply(''.join(random.sample(arg, len(arg))))

    @commands.command(aliases=['source', 'git'], help="Links my GitHub profile")
    async def github(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        embed = discord.Embed(
            title="Fripe070",
            description="[This bot is open source!](https://github.com/Fripe070/FripeBot)",
            url="https://github.com/Fripe070",
            color=ctx.author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/72686066")
        embed.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.avatar)
        if user is None:
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'{user.mention} Please take a look at my github', embed=embed)

    @commands.command(aliases=["jumbo"])
    async def emoji(self, ctx, emoji: discord.Emoji):
        if str(emoji).startswith("<a:"):
            animated = True
        else:
            animated = False
        embed = discord.Embed(timestamp=ctx.message.created_at,
                              title=f"Emoji Info",
                              description=f"""Emoji name: `{emoji.name}`
                              Emoji ID: `{emoji.id}`
                              Animated: {animated}""")

        embed.set_image(url=emoji.url)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.reply(embed=embed)
    #
    # @commands.command()
    # async def kill(self, ctx, person1=None):
    #     """Kill someone with a randomized Minecraft death message"""
    #     if person1 is None:
    #         person1 = random.choice(list(entites.values()))
    #     if "panda" in person1:
    #         await ctx.reply("How dare you try to kill a panda >:(")
    #     else:
    #         temp_message = random.choice(list(death_messages.values()))
    #         temp_message = temp_message.replace("%1$s", str(person1))
    #         temp_message = temp_message.replace("%2$s", str(ctx.author.mention))
    #         temp_message = temp_message.replace("%3$s", random.choice(list(mcitems.values())))
    #         await ctx.message.delete()
    #         await ctx.send(temp_message)
    #
    # @commands.command(aliases=["ikill"])
    # async def itemkill(self, ctx, person1=None):
    #     """Kill someone with a randomized Minecraft death message"""
    #     if person1 is None:
    #         person1 = random.choice(list(entites.values()))
    #     if "panda" in person1:
    #         await ctx.reply("How dare you try to kill a panda >:(")
    #     else:
    #         temp_message = random.choice(list(item_deaths.values()))
    #         temp_message = temp_message.replace("%1$s", str(person1))
    #         temp_message = temp_message.replace("%2$s", str(ctx.author.mention))
    #         temp_message = temp_message.replace("%3$s", random.choice(list(mcitems.values())))
    #         await ctx.message.delete()
    #         await ctx.send(temp_message)

    @commands.command(aliases=['Say'])
    @commands.is_owner()
    async def echo(self, ctx, *, tell):
        """Makes the bot say things"""
        if isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.send("That command isn't available in dms")
        else:
            await ctx.message.delete()
            await ctx.send(tell)

    @commands.command(aliases=['esay', 'embedsay'])
    @commands.is_owner()
    async def embedecho(self, ctx, *, tell):
        """Makes the bot say things"""
        if isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.send("That command isn't available in dms")
        else:
            await ctx.message.delete()
            embed = discord.Embed(title="This is a embed! :o",
                                  description=tell)
            embed.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
