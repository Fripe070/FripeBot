import discord
import requests
import random
import re
import json

from discord.ext import commands


class Help(commands.HelpCommand):
    def get_command_signature(self, command):
        return command.qualified_name

    async def send_command_help(self, command):
        embed = discord.Embed(title=f"Info about: {self.get_command_signature(command)}")
        if command.help is not None:
            embed.description(value=command.help)
        else:
            embed.description(value="This command doesnt have any further info.")
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", colour=discord.Color.blue())
        for cog, bot_commands in mapping.items():
            filtered = await self.filter_commands(bot_commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value=", ".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = Help()
        bot.help_command.cog = self

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
            name="Users:",
            value=f"{len([member for member in ctx.guild.members if not member.bot])}",
        )
        embed.add_field(
            name="Bots:",
            value=f"{len([member for member in ctx.guild.members if member.bot])}",
        )
        embed.add_field(name="Total:", value=f"{len(ctx.guild.members)}")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["def", "definition"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def define(self, ctx: commands.Context, *, word):
        """Gets the definition for a word"""
        r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", verify=True)
        if r.status_code == 200 and isinstance(r.json(), list):
            r = r.json()[0]
            print(json.dumps(r, indent=4))
            embed = discord.Embed(
                title=f"Definition of the word: {r['word']}",
                color=ctx.author.colour,
            )
            for meaning in r["meanings"]:
                tmp = ""
                if "partOfSpeech" in meaning:
                    tmp += f"{meaning['partOfSpeech']}\n"

                # if "phonetic" in r:
                #     embed_desc += f"**Pronunciation:** {r['phonetic']}\n"

                if "origin" in r:
                    tmp += f"**Origin:** {r['origin']}\n"

                if "definition" in r["meanings"][0]["definitions"][0]:
                    tmp += f"**Definition:** {r['meanings'][0]['definitions'][0]['definition']}\n"

                if "example" in r["meanings"][0]["definitions"][0]:
                    tmp += f"**Example:** {r['meanings'][0]['definitions'][0]['example']}\n"
                embed.add_field(name="Meaning:", value=tmp, inline=False)
                embed.set_footer(text=f"Source: {r['sourceUrls'][0]}")

            await ctx.reply(embed=embed)
            return

        embed = discord.Embed(
            title="Could not find a definition for that word!",
            description="Do you want to use the urban dictionary instead?",
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

    @commands.command(aliases=["wiki"])
    async def wikipedia(self, ctx, flag=None, articles=None, *, query=None):
        """Searches on Wikipedia."""
        if flag is None:
            return await ctx.reply("You need to specify a search query!")

        if flag == "-n":
            if articles.isdigit():
                if query is None:
                    return await ctx.reply("You need to specify a search query!")
                articles = int(articles)
            else:
                return await ctx.reply("You need to specify a number of articles!")
        else:
            query = f"{flag} {articles} {query}"
            articles = 5

        url = "http://en.wikipedia.org"
        data = requests.get(
            f"{url}/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
            },
        )
        if data.status_code != 200:
            return await ctx.reply("Could not connect to the wikipedia api!")
        embed = discord.Embed(title=f'Wikipedia search results for "{query}"', colour=ctx.author.colour)
        embed.set_footer(text=f"Results from {url}")
        for wiki in data.json()["query"]["search"][:articles]:
            embed.add_field(
                name=wiki["title"],
                value=f"[link]({url}?curid={wiki['pageid']})\n"
                      + re.sub(r"{\\displaystyle (.*?)}", r"\1", re.sub(r"<.*?>(.*?)<.*?>", r"\1", wiki["snippet"])),
                inline=False,
            )
        await ctx.reply(embed=embed)

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
