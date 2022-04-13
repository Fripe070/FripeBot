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
        embed = discord.Embed(
            title=msg.split(" ")[0],
            description=" ".join(msg.split(" ")[1:]),
            color=ctx.author.color,
        )
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    async def activity(self, ctx, *, activity_name=None):
        """Starts a discord activity"""
        activities = {
            "poker night": "755827207812677713",
            "betrayal.io": "773336526917861400",
            "fishington": "814288819477020702",
            "chess in the park": "832012774040141894",
            "checkers in the park": "832013003968348200",
            "blazing 8s": "832025144389533716",
            "watch together": "880218394199220334",
            "doodle crew": "878067389634314250",
            "letter league": "879863686565621790",
            "word snacks": "879863976006127627",
            "sketch heads": "902271654783242291",
            "spellcast": "852509694341283871",
            "land-io": "903769130790969345",
            "putt party": "945737671223947305",
        }

        if not activity_name:
            return await ctx.reply(
                "You need to give me an activity to launch!\nPossible activities: " + ", ".join(activities.keys())
            )
        activity_name = activity_name.lower()
        if activity_name not in activities.keys():
            return await ctx.reply("That's not a valid activity.\nPossible activities: " + ", ".join(activities.keys()))
        if ctx.author.voice is None:
            return await ctx.reply("You need to be in a voice channel to use this command.")

        invite = await ctx.author.voice.channel.create_invite(
            max_age=3600,
            target_type=discord.InviteTarget.embedded_application,
            target_application_id=activities[activity_name],
        )
        await ctx.send(invite.url)


async def setup(bot):
    await bot.add_cog(Fun(bot))
