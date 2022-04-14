import discord
import requests
import random
import re

from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def members(self, ctx: commands.Context):
        """Counts the amount of people in the server"""
        embed = discord.Embed(
            colour=ctx.author.colour,
            timestamp=ctx.message.created_at,
            title="Member Info",
        )
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        embed.add_field(
            name=f"Users:",
            value=f"{len([member for member in ctx.guild.members if not member.bot])}",
        )
        embed.add_field(
            name=f"Bots:",
            value=f"{len([member for member in ctx.guild.members if member.bot])}",
        )
        embed.add_field(name=f"Total:", value=f"{len(ctx.guild.members)}")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["def", "definition"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def define(self, ctx: commands.Context, *, word):
        """Gets the definition for a word"""
        if "-u" != word.lower().split(" ")[0] and "--urbandictionary" != word.lower().split(" ")[0]:
            r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", verify=True)
            if r.status_code == 200 and isinstance(r.json(), list):
                r = r.json()
                embed_desc = ""
                if "partOfSpeech" in r[0]["meanings"][0]:
                    embed_desc += f"{r[0]['meanings'][0]['partOfSpeech']}\n"

                if "phonetic" in r[0]:
                    embed_desc += f"**Pronunciation:** {r[0]['phonetic']}\n"

                if "origin" in r[0]:
                    embed_desc += f"**Origin:** {r[0]['origin']}\n"

                if "definition" in r[0]["meanings"][0]["definitions"][0]:
                    embed_desc += f"**Definition:** {r[0]['meanings'][0]['definitions'][0]['definition']}\n"

                if "example" in r[0]["meanings"][0]["definitions"][0]:
                    embed_desc += f"**Example:** {r[0]['meanings'][0]['definitions'][0]['example']}\n"

                embed = discord.Embed(
                    title=f"Definition of the word: {word}",
                    description=embed_desc,
                    color=ctx.author.colour,
                )
                await ctx.reply(embed=embed)
                return

            embed = discord.Embed(
                title="Could not find a definition for that word!",
                description="Do you want to use urban dictionary instead? (Results are not filtered and can be inappropriate)",
                colour=ctx.author.colour,
                timestamp=ctx.message.created_at,
            )
            askmessage = await ctx.reply(embed=embed)

            def check(reaction, user):
                return (
                    user == ctx.message.author
                    and str(reaction.emoji) == "<:yes:823202605123502100>"
                    and reaction.message == askmessage
                )

            await askmessage.add_reaction("<:yes:823202605123502100>")
            await self.bot.wait_for("reaction_add", timeout=30.0, check=check)

        else:
            word = word.split(" ")[1:]
            askmessage = None

        r = requests.get(f"https://api.urbandictionary.com/v0/define?term={word}")
        r = r.json()

        if len(r["list"]) == 0:
            embed = discord.Embed(
                title="Could not find a definition for that word!",
                colour=discord.Colour.red(),
                timestamp=ctx.message.created_at,
            )
            if askmessage is not None:
                await askmessage.clear_reaction("<:yes:823202605123502100>")
                await askmessage.edit(embed=embed)
            else:
                await ctx.reply(embed=embed)
            return

        r = r["list"][random.randint(0, len(r["list"]) - 1)]

        def sublinks(e: str):
            for i in re.findall(r"\[[^]]*]", e):
                e = e.replace(
                    i,
                    f"{i}(https://www.urbandictionary.com/define.php?term={i[1:-1].replace(' ', '+')})",
                )
            return e

        embed = discord.Embed(
            title=f"Definition of the word: {word}",
            description=f"""[**Permalink**]({r['permalink']})
Likes/Dislikes: {r['thumbs_up']}/{r['thumbs_down']}

**Definition:**
{sublinks(r['definition'])}

**Example:**
{sublinks(r['example'])}""",
        )

        embed.set_footer(text=f"Writen by: {r['author']}")
        if askmessage is not None:
            await askmessage.clear_reaction("<:yes:823202605123502100>")
            await askmessage.edit(embed=embed)
        else:
            askmessage = await ctx.reply(embed=embed)

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "🚮"

        await askmessage.add_reaction("🚮")
        await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
        await askmessage.delete()

    @commands.command()
    async def allroles(self, ctx: commands.Context):
        """Lists all roles in the server."""
        roles = [f"{role.mention} with {len(role.members)} member(s)." for role in ctx.guild.roles[1:]]
        roles.reverse()
        embed = discord.Embed(
            title=f"Roles in {ctx.guild.name}",
            description="\n".join(roles),
            colour=ctx.author.colour,
            timestamp=ctx.message.created_at,
        )
        embed.set_footer(text=f"{len(roles)} roles in total.")
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))
