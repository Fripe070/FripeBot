import discord
import random
import re
import datetime
import time

from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.snipe_message = {}

    @commands.command(help="Gives soup")
    async def soup(self, ctx: commands.Context):
        await ctx.reply("Here's your soup! <:soup:823158453022228520>")

    @commands.command(aliases=["flip"], help="Flips a coin!")
    async def coinflip(self, ctx: commands.Context):
        await ctx.reply(random.choice(["Heads!", "Tails!"]) + ":coin:")

    @commands.command(help="Rolls a dice!")
    async def dice(self, ctx: commands.Context, sides=6):
        await ctx.reply(f"You rolled a {random.randint(1, sides)}! :game_die:")

    @commands.command(aliases=["8ball"], help="A magic eightball")
    async def eightball(self, ctx: commands.Context):
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
    async def scramble(self, ctx: commands.Context, *, arg):
        await ctx.reply("".join(random.sample(arg, len(arg))))

    @commands.command(aliases=["jumbo", "emote"])
    async def emoji(self, ctx: commands.Context, emoji):
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
    async def echo(self, ctx: commands.Context, *, msg):
        """Makes the bot say things"""
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.message.delete()
        await ctx.send(msg)

    @commands.command(aliases=["esay", "embedsay", "eecho"])
    async def embedecho(self, ctx: commands.Context, *, msg):
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
    async def activity(self, ctx: commands.Context, *, activity_name=None):
        """Starts a discord activity, this requires invite permissions"""
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

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author != self.bot.user:
            self.snipe_message = {
                message.guild.id: {
                    message.channel.id: {
                        "msg": message,
                        "time": datetime.datetime.now(),
                    }
                }
            }

    @commands.command()
    async def snipe(self, ctx: commands.Context):
        """Snipes the last deleted message."""
        if (
            ctx.guild.id not in self.snipe_message.keys()
            or ctx.channel.id not in self.snipe_message[ctx.guild.id].keys()
        ):
            await ctx.reply("No message was deleted!")
            return

        snipe = self.snipe_message.get(ctx.guild.id, {}).get(ctx.channel.id, {})
        message = snipe["msg"]

        if (time.mktime(ctx.message.created_at.timetuple()) - time.mktime(snipe["time"].timetuple())) / 1000 > 10:
            await ctx.reply("That message was deleted more than 10 seconds ago!")
            return

        embed = discord.Embed(
            title=f"Message sent by {message.author.display_name} ({message.author.id})",
            description=message.content,
            timestamp=message.created_at,
            colour=message.author.colour,
        )

        if message.reference:
            try:
                ref = await ctx.fetch_message(message.reference.message_id)
                embed.add_field(
                    name=f"Replied to {ref.author.display_name} ({ref.author.id}) who said:",
                    value=ref.content,
                )
                embed.set_footer(text=f"React with 🚮 to delete this message.")
            except discord.errors.NotFound:
                embed.set_footer(
                    text="Replying to a message that doesn't exist anymore. React with 🚮 to delete this message."
                )

        if not embed.footer:
            embed.set_footer(text="React with 🚮 to delete this message.")

        snipemsg = await ctx.reply(f"Sniped message by {message.author.mention}", embed=embed)
        self.snipe_message = None

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) == "🚮" and reaction.message == snipemsg

        await snipemsg.add_reaction("🚮")
        await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        await snipemsg.delete()


async def setup(bot):
    await bot.add_cog(Fun(bot))
