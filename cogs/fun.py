import asyncio
import base64
import contextlib
import datetime
import io
import json
import math
import random
import time
from collections import defaultdict

import discord
import requests
from discord.ext import commands

from main import config
from utils import BetterEmbed


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.snipe_messages = defaultdict(dict)
        self.reddit_cache = {"subreddit": "", "posts": []}

    # noinspection SpellCheckingInspection
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
                    "Not yet",
                    "If you say so 🙃",
                    "Absolutely!",
                    "I don't think so",
                    "If you wish 😉",
                ]
            )
        )

    @commands.command()
    async def scramble(self, ctx: commands.Context, *, arg: str):
        """Scrambles the text you give it"""
        await ctx.reply("".join(random.sample(arg, len(arg))))

    @commands.command(aliases=["say"])
    async def echo(self, ctx: commands.Context, *, msg):
        """Makes the bot say things"""
        with contextlib.suppress(discord.errors.Forbidden):
            await ctx.message.delete()
        await ctx.send(msg)

    # noinspection SpellCheckingInspection
    @commands.command(aliases=["esay", "embedsay", "eecho"])
    async def embedecho(self, ctx: commands.Context, *, embed_str: str):
        """Send custom embeds through the bot."""
        try:
            embed_dict = json.loads(embed_str)
            embed = discord.Embed.from_dict(embed_dict)
            await ctx.send(embed=embed)
            with contextlib.suppress(discord.errors.Forbidden):
                await ctx.message.delete()
        except (json.JSONDecodeError, discord.HTTPException):
            await ctx.send(
                "The json you provided is invalid.\n"
                "For information about what fields discord embeds accept, visit:\n"
                "https://discord.com/developers/docs/resources/channel#embed-object."
            )

    async def save_snipe_message(self, *, message: discord.Message, current_message: discord.Message = None) -> None:
        if message.author == self.bot.user:
            return
        self.snipe_messages[message.guild.id][message.channel.id] = {
            "message": message,
            "current_message": current_message,
            "time": time.mktime(datetime.datetime.now().timetuple()),
        }

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        await self.save_snipe_message(message=message)

    @commands.Cog.listener()
    async def on_message_edit(self, old_message: discord.Message, new_message: discord.Message):
        await self.save_snipe_message(message=old_message, current_message=new_message)

    @commands.command()
    async def snipe(self, ctx: commands.Context):
        """Snipes the last deleted message."""

        # https://docs.python.org/3/glossary.html#term-EAFP
        try:
            assert list(self.snipe_messages[ctx.guild.id][ctx.channel.id].keys()) == [
                "message",
                "current_message",
                "time",
            ]
        except (KeyError, AssertionError):
            return await ctx.reply("There is no deleted/edited message to snipe.")

        sniped_message = self.snipe_messages[ctx.guild.id][ctx.channel.id]

        if time.mktime(datetime.datetime.now().timetuple()) - sniped_message["time"] > config["snipe_timeout"]:
            return await ctx.reply(
                f"The message you are trying to snipe was edited/deleted more than {config['snipe_timeout']}s ago."
            )

        message: discord.Message = sniped_message["message"]
        current_message: discord.Message = sniped_message["current_message"]
        edited = current_message is not None

        response_embed = BetterEmbed(
            title=f"Sniped message {'edit' if edited else 'deletion'} from <t:{round(sniped_message['time'])}:R>",
            colour=message.author,
        )

        response_embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
        response_embed.set_footer(text="You can react with 🚮 to delete this message.")

        if reference := message.reference:
            if reference.fail_if_not_exists and not isinstance(reference.resolved, discord.Message):
                response_embed.description += "Replying to a message that mo longer exists."
            else:
                resolved = reference.resolved
                response_embed.add_field(
                    name=f"Replying to a message by {resolved.author.display_name} ({resolved.author.id})",
                    value=reference.resolved.content,
                    inline=False,
                )

        # noinspection SpellCheckingInspection
        if message.content:
            response_embed.add_field(
                name=f"{'Original' if edited else 'Deleted'} messages content",
                value=message.content,
                inline=False,
            )

        response_embeds = [response_embed]
        files = []

        if edited:
            response_embed.add_field(
                name="New message content",
                value=current_message.content,
                inline=False,
            )
        else:
            if len(message.attachments) > 0:
                files = [await attachment.to_file() for attachment in message.attachments]

            if len(message.embeds) > 0:
                for embed in message.embeds[:9]:
                    response_embeds.append(embed)
                if len(response_embeds) - 1 < len(message.embeds):
                    response_embeds[0].add_field(
                        name="Message embeds",
                        value=f"Too many embeds to show, {len(message.embeds) - 9} has been hidden.",
                        inline=False,
                    )

        snipe_message = await ctx.reply(embeds=response_embeds, files=files)
        self.snipe_messages[ctx.guild.id][ctx.channel.id] = {}

        def check(reaction: discord.Reaction, user: discord.Member | discord.User):
            return user == message.author and str(reaction.emoji) == "🚮" and reaction.message == snipe_message

        await snipe_message.add_reaction("🚮")
        with contextlib.suppress(asyncio.exceptions.TimeoutError, discord.HTTPException):
            await self.bot.wait_for("reaction_add", timeout=60 * 5, check=check)
            await snipe_message.delete()

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
        """Converts a string into l33tspeak :sunglasses:"""
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
        """Get the bot token!!!!! (real)"""

        def random_string(length=0, key="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_0123456789"):
            return "".join(random.choice(key) for _ in range(length))

        token_id = random_string(18, "0123456789").encode("ascii")

        if random.random() < 0.15:
            await ctx.reply(f"mfa.{random_string(math.floor(random.random() * (68 - 20)) + 20)}")
            return

        encoded_id = base64.b64encode(bytes(token_id)).decode("utf-8")
        timestamp = random_string(math.floor(random.random() * (7 - 6) + 6))
        hmac = random_string(27)

        await ctx.reply(f"{encoded_id}.{timestamp}.{hmac}")

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

    @commands.command()
    async def reddit(self, ctx: commands.Context, subreddit: str):
        subreddit = subreddit.removeprefix("r/")

        if "error" in (
            response := requests.get(
                # We're heavily rate limited when using the default requests user agent
                f"https://www.reddit.com/r/{subreddit}/random.json",
                headers={"User-agent": "FripeBot"},
            ).json()
        ):
            return await ctx.reply(response["message"])
        if "error_message" in response:
            return await ctx.reply(response["error_message"])
        try:
            assert response[0]["data"]["children"][0]["data"]
        except (AssertionError, KeyError):
            return await ctx.reply(
                "Couldn't fetch any posts.\nAre you sure the specified subreddit exists? Capitalisation matters!"
            )

        post = response[0]["data"]["children"][0]["data"]
        reply_content = f"<https://www.reddit.com{post['permalink']}>\n"

        with contextlib.suppress(KeyError, TypeError):
            reply_content += post["secure_media"]["reddit_video"]["fallback_url"]
        if "url_overridden_by_dest" in post:
            reply_content += post["url_overridden_by_dest"]

        await ctx.reply(reply_content)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
