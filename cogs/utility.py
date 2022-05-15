import discord
import requests
import os
import asyncio
import random
import time
import datetime
import io
import base64
import subprocess
import re
import traceback

from discord.ext import commands
from assets.stuff import splitstring

from contextlib import redirect_stdout, redirect_stderr


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["pfpget", "gpfp", "pfp"])
    async def getpfp(self, ctx: commands.Context, user: discord.User = None):
        """Gets a users profile picture at a high resolution"""
        if not user:
            user = ctx.message.author

        embed = discord.Embed(
            colour=user.colour,
            timestamp=ctx.message.created_at,
            title=f"{user.display_name}'s pfp",
        )
        embed.set_image(url=user.display_avatar.with_size(4096).with_static_format("png"))
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    async def whois(self, ctx: commands.Context, user: discord.User = None):
        """Displays information about a discord user"""
        if not user:
            user = ctx.message.author
        user = await self.bot.fetch_user(user.id)

        embed = discord.Embed(
            title=f"User Info - {user}",
            description="",
            colour=user.colour,
            timestamp=ctx.message.created_at,
        )
        embed.description = f"**Username:** {discord.utils.escape_markdown(user.name)}\n"

        if user.mutual_guilds:
            if ctx.guild in user.mutual_guilds:
                member = ctx.guild.get_member(user.id)
            else:
                member = user.mutual_guilds[0].get_member(user.id)
        else:
            member = None

        if member and ctx.guild in user.mutual_guilds:
            embed.description += f"**Nickname:** {discord.utils.escape_markdown(user.display_name)}\n"

        embed.description += f"""**Discriminator:** #{user.discriminator}
**Mention:** {user.mention}
**ID:** {user.id}"""

        if member:
            for activity in member.activities:
                if isinstance(activity, discord.CustomActivity):
                    embed.description += f"\n**Status:** {activity}"

        embed.description += f"""
**Is user a bot:** {user.bot}
**Created at:** <t:{round(user.created_at.timestamp())}> (<t:{round(user.created_at.timestamp())}:R>)"""

        if member and ctx.guild in user.mutual_guilds:
            roles = [role.mention for role in member.roles[1:]]
            roles.reverse()
            embed.description += f"""
**Joined server at:** <t:{round(member.joined_at.timestamp())}> (<t:{round(member.joined_at.timestamp())}:R>)
**Highest Role:** {member.top_role.mention}
**Roles:** {" ".join(roles)}"""

        if user.banner:
            embed.set_image(url=user.banner.url)

        r = requests.get(
            "https://pronoundb.org/api/v1/lookup",
            params={"id": user.id, "platform": "discord"},
        )
        if r.status_code == 200:
            pronouns = {
                "hh": "he / him",
                "hi": "he / it",
                "hs": "he / she",
                "ht": "he / they",
                "ih": "it / him",
                "ii": "it / its",
                "is": "it / she",
                "it": "it / they",
                "shh": "she / he",
                "sh": "she / her",
                "si": "she / it",
                "st": "she / they",
                "th": "they / he",
                "ti": "they / it",
                "ts": "they / she",
                "tt": "they / them",
                "any": "Any pronouns",
                "other": "Other pronouns",
                "ask": "Ask me my pronouns",
                "avoid": "Avoid pronouns, use my name",
            }
            pronoun = r.json()["pronouns"]
            if not pronoun == "unspecified":
                embed.description += f"""
**Pronouns:** {pronouns[pronoun]}"""

        embed.set_thumbnail(url=user.display_avatar.with_size(4096).with_static_format("png"))
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def webget(self, ctx: commands.Context, site: str):
        if not site.startswith("http://") and not site.startswith("https://"):
            site = f"https://{site}"
        out = requests.get(site).text
        for part in splitstring(out):
            embed = discord.Embed(
                timestamp=ctx.message.created_at,
                title="Output:",
                description=f"```\n{discord.utils.escape_markdown(part)}```",
            )
            await ctx.send(embed=embed)

    @commands.command(aliases=["bash", "batch"])
    @commands.is_owner()
    async def terminal(self, ctx: commands.Context, *, args):
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        stdout, stderr = stdout.decode("utf-8"), stderr.decode("utf-8")

        try:
            embed = discord.Embed(
                title=f"Exited with code {p.returncode}.",
                colour=discord.Colour.green() if p.returncode == 0 else discord.Colour.red(),
                timestamp=ctx.message.created_at,
            )
            if stdout:
                embed.add_field(name="stdout:", value=f"```ansi\n{stdout}```", inline=False)
            if stderr:
                embed.add_field(name="stderr:", value=f"```ansi\n{stderr}```", inline=False)
            await ctx.reply(embed=embed)
        except discord.errors.HTTPException:
            for part in splitstring(stdout, 1988):
                await ctx.send(f"```ansi\n{discord.utils.escape_markdown(part)}```")

    @commands.command(aliases=["exec", "py", "python"])
    @commands.is_owner()
    async def execute(self, ctx: commands.Context, *, code):
        """Executes python code"""
        code = re.sub(r"^```(py(thon)?)?|```$", "\t", code, flags=re.IGNORECASE).strip()
        code = "\t" + code.replace("\n", "\n\t")
        function_code = f"async def __exec_code(self, ctx):\n{code}"
        with redirect_stdout(io.StringIO()) as out:
            with redirect_stderr(io.StringIO()) as err:
                exec(function_code)
                await locals()["__exec_code"](self, ctx)
        stdout = out.getvalue()
        stderr = err.getvalue()

        embed = discord.Embed(
            title="Executed:",
            description=f"```py\n{discord.utils.escape_markdown(code)}\n```".replace("\n\t", "\n"),
            timestamp=ctx.message.created_at,
            colour=ctx.author.colour,
        )
        if stdout:
            embed.add_field(name="stdout", value=f"```ansi\n{stdout}```", inline=False)
        if stderr:
            embed.add_field(name="stderr", value=f"```ansi\n{stderr}```", inline=False)

        await ctx.reply(embed=embed)
        await ctx.message.add_reaction("<:yes:823202605123502100>")

    @commands.command(aliases=["Eval"])
    @commands.is_owner()
    async def evaluate(self, ctx: commands.Context, *, arg=None):
        """Evaluates stuff"""
        if arg is None:
            await ctx.reply("I cant evaluate nothing")
            return
        # Checks if the bots token is in the output
        # This is not perfect and can easily be fooled
        # This can be done for example through encoding the token in base64
        # Or an even simpler way would be to insert a character in the middle of the token
        # Needless to say, this should not be relied on.
        if os.getenv("TOKEN") in str(eval(arg)):
            # Sends a randomly generated string that looks like a token
            await ctx.reply(
                "".join(
                    random.choices(
                        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-_",
                        k=59,
                    )
                )
            )
        else:
            await ctx.reply(eval(arg))  # Actually Evaluates
            await ctx.message.add_reaction("<:yes:823202605123502100>")

    @commands.command()
    async def remind(self, ctx: commands.Context, ae: str, *, message=None):
        """Reminds you of something in the future. Time format: H:M:S"""
        try:
            x = time.strptime(ae, "%H:%M:%S")
        except ValueError:
            return await ctx.reply("Invalid time format! Use H:M:S")
        if not message:
            return await ctx.reply("You need to specify what I should remind you about!")
        seconds = datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
        await ctx.reply(f"Ok. I will remind you about {message} in {int(seconds)}s.")
        await asyncio.sleep(seconds)
        await ctx.send(f"Hey! {ctx.author.mention}!\n{message}")

    @commands.command(aliases=["tourl"])
    async def to_url(self, ctx: commands.Context):
        """Converts attached files into urls"""
        files = [
            [await attachment.read(), attachment.content_type.split()[0]] for attachment in ctx.message.attachments
        ]
        if not files:
            return await ctx.reply("You need to give me a file!")

        attachments = [
            discord.File(
                io.BytesIO(bytes(f"data:{file[1]};base64,{base64.b64encode(file[0]).decode('utf-8')}", "utf-8")),
                filename=f"{ctx.author.name}-{ctx.author.id}-{ctx.message.created_at}.txt",
            )
            for file in files
        ]
        await ctx.reply(files=attachments, mention_author=bool(len(attachments) <= 1))


async def setup(bot):
    await bot.add_cog(Utility(bot))
