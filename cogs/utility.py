import asyncio
import base64
import datetime
import io
import re
import subprocess
import time
from contextlib import redirect_stdout

import discord
import requests
from discord.ext import commands

from assets.customfuncs import splitstring


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["pfpget", "gpfp", "pfp"])
    async def getpfp(self, ctx: commands.Context, user: discord.User = None):
        """Gets a users profile picture at a high resolution"""
        if not user:
            user = ctx.message.author

        avatar = user.display_avatar.with_size(4096).with_static_format("png")

        # This is here in case the profile picture doesn't exist, but stil gets returned by discord's api
        try:
            await avatar.read()
        except discord.errors.NotFound:
            avatar = user.default_avatar

        embed = discord.Embed(
            colour=user.colour,
            timestamp=ctx.message.created_at,
            title=f"{user.display_name}'s pfp",
        )
        embed.set_image(url=avatar)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command()
    async def whois(self, ctx: commands.Context, user: discord.User = None):
        """Displays information about a discord user"""
        if not user:
            user = ctx.message.author
        user = await self.bot.fetch_user(user.id)
        # Member object for the current guild, this should be used for stuff like nicknames
        memberhere = ctx.guild.get_member(user.id)
        # Member object for some guild, this should be used for things such as the users status
        member = user.mutual_guilds[0].get_member(user.id) if user.mutual_guilds else None

        embed = discord.Embed(
            title=f"User Info - {user}",
            colour=user.colour,
            timestamp=ctx.message.created_at,
        )
        embed.description = f"**Username:** {discord.utils.escape_markdown(user.name)}\n"
        embed.description += f"**Discriminator:** {user.discriminator}\n"
        if memberhere and memberhere.display_name != user.name:
            embed.description += f"**Nickname:** {memberhere.display_name}\n"
        embed.description += f"**Mention:** {user.mention}\n"
        embed.description += f"**ID:** {user.id}\n"
        if member:
            for activity in member.activities:
                if isinstance(activity, discord.CustomActivity):
                    embed.description += f"**Status:** {activity.emoji} {activity.name}\n"
        embed.description += f"**Is bot:** {user.bot}\n"
        embed.description += f"**Account created at:** <t:{round(user.created_at.timestamp())}> (<t:{round(user.created_at.timestamp())}:R>)\n"

        if memberhere:
            embed.description += f"**Joined server at:** <t:{round(member.joined_at.timestamp())}> (<t:{round(member.joined_at.timestamp())}:R>)\n"
            embed.description += f"**Top role:**  {[role.mention for role in memberhere.roles][1:][-1]}\n"
            embed.description += f"**Roles:**  {', '.join(reversed([role.mention for role in memberhere.roles][1:]))}\n"

        r = requests.get(
            "https://pronoundb.org/api/v1/lookup",
            params={"id": user.id, "platform": "discord"},
        )
        if r.status_code == 200:
            pronoun = r.json()["pronouns"]
            if pronoun != "unspecified":
                pronouns = {
                    "hh": "he/him",
                    "hi": "he/it",
                    "hs": "he/she",
                    "ht": "he/they",
                    "ih": "it/him",
                    "ii": "it/its",
                    "is": "it/she",
                    "it": "it/they",
                    "shh": "she/he",
                    "sh": "she/her",
                    "si": "she/it",
                    "st": "she/they",
                    "th": "they/he",
                    "ti": "they/it",
                    "ts": "they/she",
                    "tt": "they/them",
                    "any": "Any pronouns",
                    "other": "Other pronouns",
                    "ask": "Ask me my pronouns",
                    "avoid": "Avoid pronouns, use my name",
                }
                embed.description += f"**Pronouns:** {pronouns[pronoun]}\n"

        if user.banner:
            embed.set_image(url=user.banner.url)

        avatar = user.display_avatar.with_size(4096).with_static_format("png")
        # This is here in case the profile picture doesn't exist, but stil gets returned by discord's api
        try:
            await avatar.read()
        except discord.errors.NotFound:
            avatar = user.default_avatar

        embed.set_thumbnail(url=avatar)
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
                await ctx.send(f"```ansi\n{part}```")

    @commands.command(aliases=["exec", "py", "python"])
    @commands.is_owner()
    async def execute(self, ctx: commands.Context, *, code):
        """Executes python code"""
        code = re.sub(r"^```(py(thon)?\n)?|```$", "\t", code, flags=re.IGNORECASE).strip()
        code = "\t" + code.replace("\n", "\n\t")
        function_code = f"async def __exec_code(self, ctx):\n{code}"

        await ctx.message.add_reaction("<a:loading:894950036964782141>")

        with redirect_stdout(io.StringIO()) as out:
            try:
                exec(function_code)
                await locals()["__exec_code"](self, ctx)
            except Exception as e:
                stderr = e
            else:
                stderr = ""
        stdout = out.getvalue() or ""

        await ctx.message.remove_reaction("<a:loading:894950036964782141>", self.bot.user)
        await ctx.message.add_reaction("<:yes:823202605123502100>")


        embed = discord.Embed(
            title="Code executed.",
            timestamp=ctx.message.created_at,
            colour=ctx.author.colour,
        )

        if len(splitstring(stdout + stderr)) <= 1:
            if stdout != "":
                embed.add_field(name="stdout", value=f"```ansi\n{stdout}```", inline=False)
            if stderr != "":
                embed.add_field(name="stderr", value=f"```ansi\n{stderr}```", inline=False)

            await ctx.reply(embed=embed)
        else:
            pass


    @commands.command(aliases=["Eval"])
    @commands.is_owner()
    async def evaluate(self, ctx: commands.Context, *, code):
        """Evaluates one line python code"""
        code = re.sub(r"^```(py(thon)?\n)?|```$", "", code, flags=re.IGNORECASE).strip()
        code = code.split("\n")
        if len(code) > 1:
            await ctx.reply("Your code has more than one line, I will only evaluate the first line.")
        code = code[0]

        with redirect_stdout(io.StringIO()) as out:
            try:
                print(eval(code))
            except Exception as e:
                stderr = e
            else:
                stderr = None
        stdout = out.getvalue()

        embed = discord.Embed(
            title="Code evaluated.",
            timestamp=ctx.message.created_at,
            colour=ctx.author.colour,
        )
        if stdout:
            embed.add_field(name="stdout", value=f"```ansi\n{stdout}```", inline=False)
        if stderr:
            embed.add_field(name="stderr", value=f"```ansi\n{stderr}```", inline=False)

        await ctx.reply(embed=embed)
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
        """Converts attached files into base64 encoded data:// urls"""
        files = [
            [await attachment.read(), attachment.content_type.split()[0]] for attachment in ctx.message.attachments
        ]
        if not files:
            return await ctx.reply("You need to give me a file!")

        attachments = [
            discord.File(
                io.BytesIO(bytes(f"data:{file[1]}base64,{base64.b64encode(file[0]).decode('utf-8')}", "utf-8")),
                filename=f"{ctx.author.name}-{ctx.author.id}-{ctx.message.created_at}.txt",
            )
            for file in files
        ]
        await ctx.reply(files=attachments, mention_author=len(attachments) <= 1)

    @commands.command(aliases=["serverinfo"])
    async def guildinfo(self, ctx: commands.Context):
        """Shows info about the current guild"""
        guild = ctx.guild

        humans = [member for member in guild.members if not member.bot]
        bots = [member for member in guild.members if member.bot]

        embed = discord.Embed(title="Guild info", colour=ctx.author.colour, timestamp=ctx.message.created_at)
        embed.description = f"**Name:** {guild.name}\n"

        # Done like this since it might be None
        if guild.description:
            embed.description += f"**Description:** ```\n{guild.description}```\n"

        embed.description += f"""**ID:** {guild.id}
**Created at:** <t:{round(guild.created_at.timestamp())}> (<t:{round(guild.created_at.timestamp())}:R>)
**Owner:** {guild.owner.mention}
**Verification level:** {guild.verification_level}
**2FA required:** {guild.mfa_level == discord.MFALevel.require_2fa}
**Message content filter:** {str(guild.explicit_content_filter).replace('_', ' ')}
**Filesize limit:** {round(guild.filesize_limit / (1024 * 1024))}MB
**Bost level:** {guild.premium_tier} ({guild.premium_subscription_count} boosts)
"""
        # Done like this since it might be None
        if guild.premium_subscriber_role:
            embed.description += f"**Server booster role:** {guild.premium_subscriber_role.mention}\n"
        if guild.public_updates_channel:
            f"**Public updates channel:** {guild.public_updates_channel.mention}\n"
        if guild.system_channel:
            f"**System channel:** {guild.system_channel.mention}\n"
        if guild.rules_channel:
            f"**Rules channel:** {guild.rules_channel.mention}\n"

        embed.description += f"""**Prefered locale:** {guild.preferred_locale}

**Channels:** {len(guild.channels) - len(guild.categories)
        } (⌨ {len(guild.text_channels)
        } | 🔈 {len(guild.voice_channels)
        } | 🎭 {len(guild.stage_channels)
        } | 💬 {len(guild.forums)})
**Members:** {guild.member_count}/{guild.max_members} (👤 {len(humans)} | 🤖 {len(bots)})
**Emojis:** {len(guild.emojis)}/{guild.emoji_limit * 2} (🖼️ {len([
            emoji for emoji in guild.emojis if not emoji.animated
        ])}/{guild.emoji_limit} | 🎞️ {len([
            emoji for emoji in guild.emojis if emoji.animated
        ])}/{guild.emoji_limit})
**Stickers:** {len(guild.stickers)}/{guild.sticker_limit}
**Roles:** {len(guild.roles)}
**Features:** {', '.join(["`" + feature + "`" for feature in guild.features])}
"""

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if guild.banner:
            embed.set_image(url=guild.banner.url)
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))
