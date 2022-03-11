import discord
import random
import re

from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Gives soup")
    async def soup(self, ctx):
        await ctx.reply("Here's your soup! <:soup:823158453022228520>")

    @commands.command(aliases=["flip"], help="Flips a coin!")
    async def coinflip(self, ctx):
        await ctx.reply(random.choice(["Heads!", "Tails!"]) + ":coin:")

    @commands.command(help="Rolls a dice!")
    async def dice(self, ctx, sides=6):
        await ctx.reply(f"You rolled a {random.randint(1, sides)}! :game_die:")

    @commands.command(aliases=["8ball"], help="A magic eightball")
    async def eightball(self, ctx):
        await ctx.reply(
            random.choice(
                [
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
                    "If you wish 😉",
                ]
            )
        )

    @commands.command(help="Scrambles the text supplied")
    async def scramble(self, ctx, *, arg):
        await ctx.reply("".join(random.sample(arg, len(arg))))

    @commands.command(aliases=["source", "git"], help="Links my GitHub profile")
    async def github(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        embed = discord.Embed(
            title="Fripe070",
            description="[This bot is open source!](https://github.com/Fripe070/FripeBot)",
            url="https://github.com/Fripe070",
            color=ctx.author.color,
            timestamp=ctx.message.created_at,
        )
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/72686066")
        embed.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.avatar)
        if user is None:
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{user.mention} Please take a look at my github", embed=embed)

    @commands.command(aliases=["jumbo", "emote"])
    async def emoji(self, ctx, emoji):
        """Gives you info about the emoji suplied"""
        if not re.match(r"<a?:[a-zA-Z0-9_]+:[0-9]+>", emoji):
            await ctx.reply("That's not a custom emoji!")
            return

        emoji = emoji.split(":")
        emoji_id = int(emoji[2][:-1])
        emoji_name = emoji[1]
        animated = bool(emoji[0] == "<a")

        embed = discord.Embed(
            title=f"Emoji Info",
            description=f"Emoji name: `{emoji_name}`\nEmoji ID: `{emoji_id}`\nAnimated: {animated}",
            timestamp=ctx.message.created_at,
            color=ctx.author.color,
        )

        file_ext = "gif" if animated else "png"

        embed.set_image(url=f"https://cdn.discordapp.com/emojis/{emoji_id}.{file_ext}?size=4096")
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["Say"])
    @commands.is_owner()
    async def echo(self, ctx, *, msg):
        """Makes the bot say things"""
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.message.delete()
        await ctx.send(msg)

    @commands.command(aliases=["esay", "embedsay", "eecho"])
    async def embedecho(self, ctx, *, msg):
        """Makes the bot say things"""
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.message.delete()
        embed = discord.Embed(title=msg.split(" ")[0], description=" ".join(msg.split(" ")[1:]), color=ctx.author.color)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
