import json

import discord
import subprocess
import requests
import os
import asyncio
import random

from discord.ext import commands
from assets.stuff import securestring, splitstring, getpfp, senderror


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["pfpget", "gpfp", "pfp"])
    async def getpfp(self, ctx, member: discord.Member = None):
        """Gets a users profile picture at a high resolution"""
        if not member:
            member = ctx.message.author

        embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at,
                              title=f"{member.display_name}'s pfp")
        embed.set_image(url=getpfp(member))
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    # Command to get info about a account
    @commands.command()
    async def whois(self, ctx, member: discord.Member = None):
        """Displays information about a discord user"""
        if not member:
            member = ctx.message.author

        roles = [role.mention for role in member.roles[1:]]
        roles.reverse()

        embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at,
                              title=f"User Info - {member}")

        embed.set_thumbnail(url=getpfp(member))

        embed.set_footer(text=f"Requested by {ctx.author}")

        embed.add_field(name=f"Info about {member.name}", value=f"""**Username:** {securestring(member.name)}
        **Nickname:** {securestring(member.display_name)}
        **Mention:** {member.mention}
        **ID:** {member.id}
        **Account Created At:** {member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")}
        **Joined server at:** {member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")}
        **Is user on mobile:** {member.is_on_mobile()}
        **Highest Role:** {member.top_role.mention}

        **Roles:** {" ".join(roles)}""")
#            **Activity:** {afunctionthatfroopwants(member.activity.name)}
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def webget(self, ctx, site: str):
        if not site.startswith("http://") and not site.startswith("https://"):
            site = f"https://{site}"
        out = requests.get(site).text
        for part in splitstring(out):
            embed = discord.Embed(timestamp=ctx.message.created_at,
                                  title=f"Output:",
                                  description=f"```\n{securestring(part)}```")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def bash(self, ctx, *, args):
        proc = await asyncio.create_subprocess_shell(f"/bin/bash -c '{args}'", stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()

        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')

        print(stdout)
        print(stderr)
        for part in splitstring(stdout, 1993):
            await ctx.send(f"```\n{part}```")

    @commands.command(aliases=['Exec'])
    @commands.is_owner()
    async def execute(self, ctx, *, code):
        """Executes python code"""
        if len(code) == 0:
            await ctx.reply("I cant execute nothing")
            return
        code = code.replace('```py', '').replace('```', '').strip()
        code = '\n'.join([f'\t{line}' for line in code.splitlines()])
        function_code = (
            'async def __exec_code(self, ctx):\n'
            f'{code}')
        try:
            exec(function_code)
            output = await locals()['__exec_code'](self, ctx)
            if output:
                formatted_output = '\n    '.join(output) if len(code.splitlines()) > 1 else output
                await ctx.reply(embed=discord.Embed(colour=0xff0000,
                                                    timestamp=ctx.message.created_at,
                                                    title="Your code ran successfully!",
                                                    description=f"```\n{formatted_output}\n```"))
            await ctx.message.add_reaction("<:yes:823202605123502100>")
        except Exception as error:
            await senderror(ctx, error)

    @commands.command(aliases=['Eval'])
    @commands.is_owner()
    async def evaluate(self, ctx, *, arg=None):
        """Evaluates stuff"""
        if arg is None:
            await ctx.reply("I cant evaluate nothing")
            return
        # Checks if the bots token is in the output
        if os.getenv('TOKEN') in str(eval(arg)):
            # Sends a randomly generated string that looks like a token
            await ctx.reply(''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-_", k=59)))
        else:
            try:
                await ctx.reply(eval(arg))  # Actually Evaluates
                await ctx.message.add_reaction("<:yes:823202605123502100>")
            except Exception as error:
                await senderror(ctx, error)

    @commands.command()
    async def members(self, ctx):
        """Counts the amount of people in the server"""
        embed = discord.Embed(colour=ctx.author.colour, timestamp=ctx.message.created_at, title="Member Info")
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        embed.add_field(name=f"Users:", value=f"{len([member for member in ctx.guild.members if not member.bot])}")
        embed.add_field(name=f"Bots:", value=f"{len([member for member in ctx.guild.members if member.bot])}")
        embed.add_field(name=f"Total:", value=f"{len(ctx.guild.members)}")
        await ctx.reply(embed=embed)

    # Command to get the bots ping
    @commands.command()
    async def ping(self, ctx):
        """Displays the bots ping"""
        await ctx.message.add_reaction("🏓")
        bot_ping = round(self.bot.latency * 1000)
        if bot_ping < 130:
            color = 0x44ff44
        elif bot_ping > 130 and bot_ping < 180:
            color = 0xff8c00
        else:
            color = 0xff2200
        embed = discord.Embed(title="Pong! :ping_pong:",
                              description=f"The ping is **{bot_ping}ms!**",
                              color=color)
        await ctx.reply(embed=embed)

    @commands.command(aliases=['def', 'definition'])
    async def define(self, ctx, *, word):
        """Gets the defenition for a word"""
        embed = discord.Embed(title=f"Defenition of the word: {word}")

        try:
            resp = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en_GB/{word}')
            resp = resp.json()
            resp = resp[0]["meanings"]
            for i in resp:
                for e in i["definitions"][:2]:
                    try:
                        embed.add_field(name=i["partOfSpeech"],
                                        value=f'**Defenition:** ```{e["definition"]}```\n**Example:** ```{e["example"]}```')
                    except KeyError:
                        try:
                            embed.add_field(name=i["partOfSpeech"], value=f'Defenition: ```{e["definition"]}```')
                        except KeyError:
                            embed.add_field(name="e", value=f'Defenition: ```{e["definition"]}```')
            await ctx.reply(embed=embed)
        except KeyError:
            embed = discord.Embed(title="Could not find a defenition for that word!",
                                  description="Do you want to use urban dictionary instead? (Results are not filtered and can be inappropriate)",
                                  colour=ctx.author.colour,
                                  timestamp=ctx.message.created_at
                                  )
            askmessage = await ctx.reply(embed=embed)

            yesemoji = "<:yes:823202605123502100>"

            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == yesemoji

            await askmessage.add_reaction(yesemoji)
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
            except TimeoutError:
                pass
            else:
                resp = requests.get(f"https://api.urbandictionary.com/v0/define?term={word}")

                resp = resp.json()

                resp = resp["list"][0]

                embed = discord.Embed(
                    title=f"Defenition of the word: {word}",
                    description=f"""[**Permalink**]({resp['permalink']})
Likes/Dislikes: {resp['thumbs_up']}/{resp['thumbs_down']}

**Definition:**
{resp['definition'].replace('[', '').replace(']', '')}

**Example:**
{resp['example'].replace('[', '').replace(']', '')}"""
                )

                embed.set_footer(text=f"Writen by: {resp['author']}")
                print(resp)
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
