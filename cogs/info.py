import random
import re

import discord
import requests
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def members(self, ctx: commands.Context):
        """Counts the amount of people in the server"""
        users = len([member for member in ctx.guild.members if not member.bot])
        bots = len([member for member in ctx.guild.members if member.bot])
        embed = discord.Embed(
            title="Member Info",
            description=f"**Bot/user ratio:** {round(bots/users, 2)} bots for each human",
            colour=ctx.author.colour,
            timestamp=ctx.message.created_at,
        )
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        embed.add_field(
            name="Users:",
            value=f"{users}",
        )
        embed.add_field(
            name="Bots:",
            value=f"{bots}",
        )
        embed.add_field(name="Total:", value=f"{len(ctx.guild.members)}")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["def", "definition"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def define(self, ctx: commands.Context, *, word):
        """Gets the definition for a word"""
        r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", verify=True)
        fields = []
        if r.status_code == 200 and isinstance(r.json(), list):
            r = r.json()
            embed = discord.Embed(
                title=f"Definition of the word: {r[0]['word']}",
                color=ctx.author.colour,
            )
            for i in r:
                for meaning in i["meanings"]:
                    for definition in meaning["definitions"][:2]:
                        if len(fields) >= 6:
                            break
                        synonyms = list(meaning["synonyms"])
                        for defs in meaning["definitions"]:
                            for synonym in defs["synonyms"]:
                                synonyms.append(synonym)
                        field = [
                            meaning["partOfSpeech"],
                            f"""
{'**Pronunciation:** ' + meaning['phonetic'] if 'phonetic' in meaning else ''}
**Definition:** {definition['definition']}
{'**Example:** ' + definition['example'] if 'example' in definition else ''}
{'**Synonyms:** ' + ', '.join(synonyms) if synonyms else ''}""".replace(
                                "\n\n", "\n"
                            ),
                        ]
                        if field not in fields:
                            fields.append(field)

            for field in fields:
                embed.add_field(name=field[0], value=field[1])

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
            if not articles.isdigit():
                return await ctx.reply("You need to specify a number of articles!")
            if query is None:
                return await ctx.reply("You need to specify a search query!")
            articles = int(articles)
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
                + re.sub(r"{\\displaystyle (.*?)}", r"\1", re.sub(r"<.*?>(.*?)<.*?>", r"\1", wiki["snippet"])).replace(
                    "&quot;", '"'
                ),
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

    @commands.command()
    async def pep(self, ctx: commands.Context, pep: int = 0):
        """Send the link to the specified python pep."""
        url = f"https://peps.python.org/pep-{pep:04d}"
        r = requests.head(url)
        if r.status_code == 404:
            return await ctx.reply("That PEP doesn't exist.")
        await ctx.reply(url)

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

        if memberhere is not None:
            avatar_user = memberhere
        elif member is not None:
            avatar_user = member
        else:
            avatar_user = user
        avatar = avatar_user.display_avatar.with_size(4096).with_static_format("png")

        # This is here in case the profile picture doesn't exist, but stil gets returned by discord's api
        try:
            await avatar.read()
        except discord.errors.NotFound:
            avatar = user.default_avatar

        embed.set_thumbnail(url=avatar)
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.send(embed=embed)

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

    @commands.command(aliases=["pfpget", "gpfp", "pfp"])
    async def getpfp(self, ctx: commands.Context, user: discord.User = None):
        """Gets a users profile picture at a high resolution"""
        if not user:
            user = ctx.message.author

        global_avatar = user.avatar.with_size(4096).with_static_format("png")

        # This is here in case the profile picture doesn't exist, but stil gets returned by discord's api
        try:
            await global_avatar.read()
        except discord.errors.NotFound:
            global_avatar = user.default_avatar

        global_avatar_embed = discord.Embed(
            colour=user.colour,
            timestamp=ctx.message.created_at,
            title=f"{user.display_name}'s pfp",
        )
        global_avatar_embed.set_image(url=global_avatar)
        global_avatar_embed.set_footer(text=f"Requested by {ctx.author}")
        embeds = [global_avatar_embed]

        memberhere = ctx.guild.get_member(user.id)
        member = user.mutual_guilds[0].get_member(user.id) if user.mutual_guilds else None
        if memberhere is not None:
            new_user = memberhere
        elif member is not None:
            new_user = member
        else:
            new_user = user
        local_avatar = new_user.display_avatar.with_size(4096).with_static_format("png")
        try:
            await local_avatar.read()
        except discord.errors.NotFound:
            local_avatar = user.default_avatar

        if global_avatar != local_avatar:
            local_avatar_embed = discord.Embed(
                colour=user.colour,
                timestamp=ctx.message.created_at,
                title=f"{new_user.display_name}'s server specific pfp",
            )
            local_avatar_embed.set_image(url=local_avatar)
            local_avatar_embed.set_footer(text=f"Requested by {ctx.author}")
            embeds.append(local_avatar_embed)

        await ctx.send(embeds=embeds)

    @commands.command(aliases=["bannerget", "banner"])
    async def getbanner(self, ctx: commands.Context, user: discord.User = None):
        """Gets a users banner picture at a high resolution"""
        if user is None:
            user = ctx.message.author

        user = await self.bot.fetch_user(user.id)

        banner = user.banner
        if banner is None:
            return await ctx.reply("That user doesn't have a banner.")
        banner = banner.with_size(4096).with_static_format("png")

        embed = discord.Embed(
            colour=user.colour,
            timestamp=ctx.message.created_at,
            title=f"{user.display_name}'s banner",
        )
        embed.set_image(url=banner)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["jumbo", "emote"])
    async def emoji(self, ctx: commands.Context, emoji: str):
        """Gives you info about the emoji suplied"""
        if not re.match(r"`?\\?<a?:\w+:\d+>`?", emoji, flags=re.ASCII):
            await ctx.reply("That's not a custom emoji!")
            return

        emoji = emoji.split(":")
        emoji_id = re.search("[0-9]+", emoji[2])[0]
        print(emoji_id)
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

    @commands.command(aliases=["getmsg", "raw", "rawmsg"])
    async def getraw(self, ctx: commands.Context, msg: int | str = None):
        """Returns the raw message being linked"""
        if isinstance(msg, int):
            message = await ctx.channel.fetch_message(msg)
        elif msg_link_regex := re.match(
            f"https://.*discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/([0-9]+)", str(msg)
        ):
            message = await ctx.channel.fetch_message(msg_link_regex[1])
        elif msg is None and ctx.message.reference and ctx.message.reference.fail_if_not_exists:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        else:
            return await ctx.reply("You need to provide me with a message, either through an id. link or a reply")

        await ctx.send(discord.utils.escape_markdown(message.content))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Info(bot))
