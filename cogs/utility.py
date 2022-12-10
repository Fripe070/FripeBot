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
        function_code = f"async def __exec_code(self, ctx):\n\tbot = self.bot\n{code}"

        await ctx.message.add_reaction("<a:loading:894950036964782141>")

        with redirect_stdout(io.StringIO()) as out:
            try:
                exec(function_code)
                await locals()["__exec_code"](self, ctx)
            except Exception as e:
                stderr = e
            else:
                stderr = None
        stdout = out.getvalue() or None

        await ctx.message.remove_reaction("<a:loading:894950036964782141>", self.bot.user)
        await ctx.message.add_reaction("<:yes:823202605123502100>")

        title = "Code executed "
        if stderr is not None:
            title += f"with an exeption: `{type(stderr).__name__}`"

        embed = discord.Embed(
            title=title,
            timestamp=ctx.message.created_at,
            colour=discord.Colour.red() if stderr else discord.Colour.green(),
        )

        if stdout is not None:
            embed.add_field(name="stdout:", value=f"```ansi\n{stdout}```", inline=False)
        if stderr is not None:
            embed.add_field(name="stderr:", value=f"```ansi\n{stderr}```", inline=False)

        await ctx.reply(embed=embed)

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

        title = "Code evaluated "
        if stderr is not None:
            title += f"with an exeption: `{type(stderr).__name__}`"
        embed = discord.Embed(
            title=title,
            timestamp=ctx.message.created_at,
            colour=discord.Colour.red() if stderr else discord.Colour.green(),
        )
        if stdout:
            embed.add_field(name="stdout:", value=f"```ansi\n{stdout}```", inline=False)
        if stderr:
            embed.add_field(name="stderr:", value=f"```ansi\n{stderr}```", inline=False)

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


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utility(bot))
