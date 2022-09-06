import base64
import contextlib
import datetime
import json
import math
import random
import re
import time

import discord
import requests
from discord.ext import commands

from assets.customfuncs import randomstring
from main import config


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.snipe_message = {}

    @commands.command(aliases=["tc"])
    async def tagcreate(self, ctx: commands.Context, name: str, *, content: str):
        config["tags"][name] = content
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        await ctx.reply("Tag added.")

    @commands.command(aliases=["t"])
    async def tag(self, ctx: commands.Context, name: str):
        if name not in config["tags"]:
            return await ctx.reply("There is no tag with that name.")

        with contextlib.suppress(discord.errors.Forbidden):
            await ctx.message.delete()
        await ctx.send(config["tags"][name])

    @commands.command()
    async def soup(self, ctx: commands.Context):
        """Gives you some soup"""
        await ctx.reply("Here's your soup! <:soup:823158453022228520>")

    @commands.command()
    async def coinflip(self, ctx: commands.Context):
        """Flips a coin!"""
        await ctx.reply(random.choice(["Heads!", "Tails!"]) + " :coin:")

    @commands.command()
    async def dice(self, ctx: commands.Context, sides: int = 6, sides2: int = None):
        """Rolls a die with the specified number of sides"""
        if sides == 0 or sides2 == 0:
            return await ctx.reply("Sides cannot be 0.")
        if sides2 and sides2 < sides:
            return await ctx.reply("The first argument must be lower than the second.")

        number = random.randint(1 if sides2 is None else sides, sides if sides2 is None else sides2)
        await ctx.reply(f"You rolled a {number}! :game_die:")

    @commands.command(aliases=["8ball"])
    async def eightball(self, ctx: commands.Context):
        """A magic eightball!"""
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

    @commands.command()
    async def scramble(self, ctx: commands.Context, *, arg):
        """Scrambles the text you give it"""
        await ctx.reply("".join(random.sample(arg, len(arg))))

    @commands.command(aliases=["jumbo", "emote"])
    async def emoji(self, ctx: commands.Context, emoji):
        """Gives you info about the emoji suplied"""
        if not re.match(r"<a?:\w+:\d+>", emoji, flags=re.ASCII):
            await ctx.reply("That's not a custom emoji!")
            return

        emoji = emoji.split(":")
        emoji_id = int(emoji[2][:-1])
        emoji_name = emoji[1]
        animated = emoji[0] == "<a"

        embed = discord.Embed(
            title="Emoji Info",
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
        with contextlib.suppress(discord.errors.Forbidden):
            await ctx.message.delete()
        await ctx.send(msg)

    @commands.command(aliases=["esay", "embedsay", "eecho"])
    async def embedecho(self, ctx: commands.Context, *, msg):
        """Makes the bot say things"""
        with contextlib.suppress(discord.errors.Forbidden):
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
                        "old_msg": message,
                        "new_msg": None,
                        "time": time.mktime(datetime.datetime.now().timetuple()),
                    }
                }
            }

    @commands.Cog.listener()
    async def on_message_edit(self, old_message: discord.Message, new_message: discord.Message):
        if old_message.author != self.bot.user:
            self.snipe_message = {
                old_message.guild.id: {
                    old_message.channel.id: {
                        "old_msg": old_message,
                        "new_msg": new_message,
                        "time": time.mktime(datetime.datetime.now().timetuple()),
                    }
                }
            }

    @commands.command()
    async def snipe(self, ctx: commands.Context):
        """Snipes the last deleted message."""
        if (
            not self.snipe_message
            or ctx.guild.id not in self.snipe_message.keys()
            or ctx.channel.id not in self.snipe_message[ctx.guild.id].keys()
            or self.snipe_message[ctx.guild.id][ctx.channel.id] is None
        ):
            await ctx.reply("No message was deleted/edited.")
            return

        snipe = self.snipe_message.get(ctx.guild.id, {}).get(ctx.channel.id, {})

        if time.mktime(datetime.datetime.now().timetuple()) - snipe["time"] > config["snipetimeout"]:
            await ctx.reply(
                f"The message you are trying to snipe was {'edited' if snipe['new_msg'] else 'deleted'} more than {config['snipetimeout']} seconds ago. "
            )
            return

        old_message = snipe["old_msg"]
        new_message = snipe["new_msg"]

        embed = discord.Embed(
            title=f"Message sent by {old_message.author.display_name} ({old_message.author.id})",
            description=old_message.content,
            timestamp=old_message.created_at,
            colour=old_message.author.colour,
        )

        if old_message.reference:
            try:
                ref = await ctx.fetch_message(old_message.reference.message_id)
                embed.add_field(
                    name=f"Replied to {ref.author.display_name} ({ref.author.id}) who said:", value=ref.content
                )

            except discord.errors.NotFound:
                embed.set_footer(
                    text="Replying to a message that doesn't exist anymore."
                    if old_message.author.id in config["snipeblock"]
                    else "Replying to a message that doesn't exist anymore. React with 🚮 to delete this message."
                )
        if snipe["new_msg"]:
            embed.add_field(name="Orignal", value=new_message.content, inline=False)

        if not embed.footer and old_message.author.id not in config["snipeblock"]:
            embed.set_footer(text="React with 🚮 to delete this message.")

        snipemsg = await ctx.reply(
            f"Sniped {'edited' if snipe['new_msg'] else 'deleted'} message by {old_message.author.mention}",
            embed=embed,
        )

        self.snipe_message[ctx.guild.id][ctx.channel.id] = None

        if old_message.author.id in config["snipeblock"]:
            return

        def check(reaction, user):
            return user == old_message.author and str(reaction.emoji) == "🚮" and reaction.message == snipemsg

        await snipemsg.add_reaction("🚮")
        await self.bot.wait_for("reaction_add", timeout=60 * 5, check=check)
        await snipemsg.delete()

    @commands.command()
    async def unsplash(self, ctx: commands.Context, query: str = "bread"):
        """Searches for a random image on unsplash.com. Defaults to bread."""
        await ctx.send(requests.get(f"https://source.unsplash.com/random/?{query}").url)

    @commands.command(aliases=["mock"])
    async def varied(self, ctx: commands.Context, *, msg: str):
        """MaKeS a StRiNgS cApItAlIsAtIoN vArIeD"""
        varied = ""
        i = True  # capitalize
        for char in msg:
            varied += char.upper() if i else char.lower()
            if char != " ":
                i = not i

        await ctx.reply(varied)

    @commands.command(aliases=["l33t", "leetspeak"])
    async def leet(self, ctx: commands.Context, *, msg: str):
        """Converts a string into leetspeak"""
        msg = msg.lower()
        l33t = msg.maketrans(
            {
                "a": "4",
                "e": "3",
                "i": "1",
                "l": "1",
                "o": "0",
                "z": "2",
                "b": "8",
            }
        )

        await ctx.reply(msg.translate(l33t))

    @commands.command(aliases=["reverse", "reversed", "flipped"])
    async def flip(self, ctx: commands.Context, *, msg: str):
        """Flips a string"""
        await ctx.reply(msg[::-1])

    @commands.command()
    async def token(self, ctx: commands.Context):
        """Gets a (very real) token!!!"""
        tokenid = randomstring(18, "0123456789").encode("ascii")

        if random.random() < 0.15:
            return f"mfa.{randomstring(math.floor(random.random() * (68 - 20)) + 20)}"
        encodedid = base64.b64encode(bytes(tokenid)).decode("utf-8")
        timestamp = randomstring(math.floor(random.random() * (7 - 6) + 6))
        hmac = randomstring(27)

        await ctx.reply(f"{encodedid}.{timestamp}.{hmac}")


async def setup(bot):
    await bot.add_cog(Fun(bot))
