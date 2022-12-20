import asyncio
import base64
import contextlib
import datetime
import io
import json
import math
import random
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
    @commands.is_owner()
    async def tagcreate(self, ctx: commands.Context, name: str, *, content: str):
        config["tags"][name] = content
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        await ctx.reply("Tag added.")

    @commands.command(aliases=["t", "tags"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tag(self, ctx: commands.Context, name: str = None):
        if name is None:
            embed = discord.Embed(title="Tags:", description=", ".join(config["tags"].keys()), colour=ctx.author.colour)
            return await ctx.send(embed=embed)
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
    async def scramble(self, ctx: commands.Context, *, arg: str):
        """Scrambles the text you give it"""
        await ctx.reply("".join(random.sample(arg, len(arg))))

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

        old_message = snipe["old_msg"]
        new_message = snipe["new_msg"]

        if time.mktime(datetime.datetime.now().timetuple()) - snipe["time"] > config["snipetimeout"]:
            await ctx.reply(
                f"The message you are trying to snipe was {'edited' if new_message else 'deleted'} more than {config['snipetimeout']} seconds ago. "
            )
            return

        embed = discord.Embed(
            title=f"Message {'edited' if new_message else 'deleted'} <t:{round(snipe['time'])}:R>",
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
        if new_message is not None:
            embed.add_field(name="Orignal:", value=old_message.content, inline=False)
            embed.add_field(name="New:", value=new_message.content, inline=False)
        else:
            embed.description = old_message.content

        if not embed.footer and old_message.author.id not in config["snipeblock"]:
            embed.set_footer(text="React with 🚮 to delete this message.")

        snipemsg = await ctx.reply(
            f"Sniped {'edited' if new_message else 'deleted'} message by {old_message.author.mention}",
            embed=embed,
        )

        self.snipe_message[ctx.guild.id][ctx.channel.id] = None

        if old_message.author.id in config["snipeblock"]:
            return

        def check(reaction, user):
            return user == old_message.author and str(reaction.emoji) == "🚮" and reaction.message == snipemsg

        await snipemsg.add_reaction("🚮")
        with contextlib.suppress(asyncio.exceptions.TimeoutError):
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

    @commands.command(aliases=["aigen", "aiimg", "imggen"])
    async def stablehorde(self, ctx: commands.Context, seed: int | str, *, prompt: str = ""):
        """Uses AI to generate an image with the stable horde API."""
        if isinstance(seed, str):
            prompt = f"{seed} {prompt}"
            seed = None
        if prompt == "":
            return await ctx.reply("You need to provide a prompt.")

        models = [
            "stable_diffusion",
            "waifu_diffusion",
            "Anything Diffusion",
        ]
        model = random.choice(models)

        base_url = "https://stablehorde.net/api"
        r = requests.post(
            f"{base_url}/v2/generate/async",
            headers={"apikey": config["stable_horde"]},
            json={
                "prompt": prompt,
                "params": {"height": 512, "width": 512, "steps": 40, "n": 1},
                "nsfw": True,  # Very sensitive, thus I rely on cencoring rather than flat out blocking
                "censor_nsfw": True,
                "trusted_workers": False,
                "models": [model],
            },
        )
        if r.status_code != 202:
            return await ctx.reply(f"API returned status code {r.status_code}: {r.json()['message']}")

        generation_id = r.json()["id"]

        embed = discord.Embed(
            title="Generating image...",
            description=f"""
**Prompt:** {discord.utils.escape_markdown(prompt)}
**Seed:** {seed if seed is not None else 'random'}
**Model:** {model.replace("_", " ").title()}
""",
            colour=ctx.author.colour,
        )
        embed.add_field(name="Status", value="Initialising...")
        msg = await ctx.reply(embed=embed)

        # Using a for loop here rather than a while loop, so it aborts after 5 minutes of no img being returned
        for _ in range(60 * 5):
            r = requests.get(f"{base_url}/v2/generate/check/{generation_id}").json()

            embed.remove_field(0)
            embed.add_field(
                name="Status",
                value=f"""
**Images finished:** {r["finished"]}
**Estimated to be done:** <t:{round(time.time()) + r["wait_time"]}:R>
**Queue position:** {r["queue_position"]}
**State:** {"Processing" if r["processing"] else "Waiting"}
""",
            )
            await msg.edit(embed=embed)

            # Stop if the image is ready
            if r["done"]:
                break
            await asyncio.sleep(1)

        r = requests.get(f"{base_url}/v2/generate/status/{generation_id}").json()["generations"]
        embed = discord.Embed(title=f"Image{'s' if len(r) > 1 else ''} generated.", colour=ctx.author.colour)
        embed.description = f"**Prompt:** {discord.utils.escape_markdown(prompt)}" + "\n"
       
        if len(r) > 1:
            embed.description += (
                "**Seeds:** " + ", ".join([f"`{gen['seed']}`" for gen in r]) + " (random)\n" if seed is None else "\n"
            )
        else:
            embed.description += f"**Seed:** `{r[0]['seed']}` {'(random)' if seed is None else ''}" + "\n"

        embed.description += f"**Model:** {r[0]['model'].replace('_', ' ').title()}"

        embed.set_footer(text=f"React with 🚮 to delete {'these images' if len(r) > 1 else 'this image'}.")
        files = [discord.File(io.BytesIO(base64.b64decode(gen["img"])), filename="image.webp") for gen in r]
        await msg.edit(embed=embed, attachments=files)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
