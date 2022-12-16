import contextlib
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Optional, Union, Any

import discord
from discord import Object, utils
from discord.abc import Snowflake
from discord.ext import commands
from discord.ext.commands import Context
from discord.object import OLDEST_OBJECT


# Code from the discord.py source code, but with a singular line changed :D
# danny pls add to d.py :)
async def raw_history(
    self,
    *,
    limit: Optional[int] = 100,
    before: Optional[Union["Snowflake", datetime]] = None,
    after: Optional[Union["Snowflake", datetime]] = None,
    around: Optional[Union["Snowflake", datetime]] = None,
    oldest_first: Optional[bool] = None,
) -> AsyncIterator[dict]:
    async def _around_strategy(retrieve: int, around: Optional[Snowflake], limit: Optional[int]):
        if not around:
            return []

        around_id = around.id if around else None
        data = await self._state.http.logs_from(channel.id, retrieve, around=around_id)

        return data, None, limit

    async def _after_strategy(retrieve: int, after: Optional[Snowflake], limit: Optional[int]):
        after_id = after.id if after else None
        data = await self._state.http.logs_from(channel.id, retrieve, after=after_id)

        if data:
            if limit is not None:
                limit -= len(data)

            after = Object(id=int(data[0]["id"]))

        return data, after, limit

    async def _before_strategy(retrieve: int, before: Optional[Snowflake], limit: Optional[int]):
        before_id = before.id if before else None
        data = await self._state.http.logs_from(channel.id, retrieve, before=before_id)

        if data:
            if limit is not None:
                limit -= len(data)

            before = Object(id=int(data[-1]["id"]))

        return data, before, limit

    if isinstance(before, datetime):
        before = Object(id=utils.time_snowflake(before, high=False))
    if isinstance(after, datetime):
        after = Object(id=utils.time_snowflake(after, high=True))
    if isinstance(around, datetime):
        around = Object(id=utils.time_snowflake(around))

    reverse = after is not None if oldest_first is None else oldest_first
    after = after or OLDEST_OBJECT
    predicate = None

    if around:
        if limit is None:
            raise ValueError("history does not support around with limit=None")
        if limit > 101:
            raise ValueError("history max limit 101 when specifying around parameter")

        # Strange Discord quirk
        limit = 100 if limit == 101 else limit

        strategy, state = _around_strategy, around

        if before and after:
            predicate = lambda m: after.id < int(m["id"]) < before.id
        elif before:
            predicate = lambda m: int(m["id"]) < before.id
        elif after:
            predicate = lambda m: after.id < int(m["id"])
    elif reverse:
        strategy, state = _after_strategy, after
        if before:
            predicate = lambda m: int(m["id"]) < before.id
    else:
        strategy, state = _before_strategy, before
        if after and after != OLDEST_OBJECT:
            predicate = lambda m: int(m["id"]) > after.id

    channel = await self._get_channel()

    while True:
        retrieve = min(100 if limit is None else limit, 100)
        if retrieve < 1:
            return

        data, state, limit = await strategy(retrieve, state, limit)

        # Terminate loop on next iteration; there's no data left after this
        if len(data) < 100:
            limit = 0

        if reverse:
            data = reversed(data)
        if predicate:
            data = filter(predicate, data)

        for raw_message in data:
            yield raw_message


discord.abc.Messageable.raw_history = raw_history


async def log_and_send(content: str, logger: logging.Logger, message: discord.Message | Context) -> discord.Message:
    if isinstance(message, Context):
        msg = await message.send(content=content)
    else:
        msg = await message.edit(content=content)
    logger.info(content)
    return msg


async def get_messages(channel: discord.abc.GuildChannel | discord.abc.Messageable, /, message_limit: int = None) -> list:
    # If this ever errors, I blame future fripe.
    self_perms = channel.permissions_for(channel.guild.me)
    if self_perms.read_messages and self_perms.read_message_history and hasattr(channel, "history"):
        # Reasoning for me not using the get_object_atrs function:
        # There can easily be millions of messages, any non-essential parsing will slow it down noticeably.
        return [message async for message in channel.history(limit=message_limit)]
    return []


# This is a bit uggly looking, but it's infinately better than specifying each key: value pair by hand
async def get_object_atrs(obj: Any, /, check: callable = None) -> dict:
    return_dict = {}
    for name in dir(obj):
        # We have no need for these
        if name.startswith("_"):
            continue

        value = getattr(obj, name)
        # We don't care about the atribute if it's a method or function
        if callable(value):
            continue

        # Perform our custom check
        if check is not None:
            result = await check(name, value)
            if result is not None:
                if isinstance(result, tuple) and len(result) == 2:
                    name, value = result
                else:
                    value = result
                return_dict[name] = value
                continue

        allowed_standad_types = (str, int, float, bool, type(None))
        # Elif chain my beloved
        if (
            isinstance(value, allowed_standad_types)
            or (isinstance(value, (list, tuple)) and all(type(i) in allowed_standad_types for i in value))
            or value.__class__.__module__
            in [
                "discord.enums",
            ]
        ):
            return_dict[name] = value
        elif isinstance(value, set) and all(type(i) in allowed_standad_types for i in value):
            return_dict[name] = list(value)
        elif isinstance(value, datetime):
            return_dict[name] = time.mktime(value.timetuple())
        elif isinstance(value, discord.asset.Asset):
            return_dict[name] = value.url
        elif isinstance(value, discord.SystemChannelFlags):
            return_dict[name] = value.value
        elif isinstance(
            value,
            (discord.member.Member, discord.User, discord.role.Role, discord.abc.GuildChannel, discord.Guild),
        ):
            return_dict[name] = value.id
        elif isinstance(value, (discord.Colour, discord.Permissions)):
            return_dict[name] = value.value

    return return_dict


async def get_guild_data(guild: discord.Guild) -> dict:
    async def check(name, value):
        if isinstance(value, list):
            return_value = await get_object_atrs(value)
            return return_value
        return None

    atrs = await get_object_atrs(guild, check=check)

    return atrs


async def get_emojis(guild: discord.Guild) -> list:
    emojis = []
    for emoji in guild.emojis:

        async def check(name, value):
            if isinstance(value, list):
                return_value = await get_object_atrs(value)
                return return_value
            return None

        atrs = await get_object_atrs(emoji, check=check)
        emojis.append(atrs)

    return emojis


async def get_stickers(guild: discord.Guild) -> list:
    return [await get_object_atrs(sticker) for sticker in guild.stickers]


async def get_members(guild: discord.Guild) -> list:
    members = []

    async for member in guild.fetch_members(limit=None):
        member = guild.get_member(member.id)

        async def check(name, value):
            if isinstance(value, (list, tuple)):
                return_value = await get_object_atrs(value, check=check)
                return return_value
            elif isinstance(value, (discord.Colour, discord.PublicUserFlags, discord.Permissions)):
                return value.value
            elif value.__class__.__module__ == "discord.activity":
                return value.to_dict()
            return None

        with contextlib.suppress(AttributeError):
            atrs = await get_object_atrs(member, check=check)
            members.append(atrs)

    return members


async def get_roles(guild: discord.Guild) -> list:
    roles = []

    for role in guild.roles:

        async def check(name, value):
            if isinstance(value, list) and all(isinstance(item, discord.Member) for item in value):
                return [member.id for member in value]
            if isinstance(value, discord.RoleTags):
                return await get_object_atrs(value, check=check)
            if isinstance(value, discord.utils.SequenceProxy):
                tmp_return = [await get_object_atrs(i) for i in value]
                return tmp_return
            return None

        atrs = await get_object_atrs(role, check=check)
        roles.append(atrs)

    return roles


class Scraping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_channels(
        self, guild: discord.Guild, /, message_limit: int = 100, log_message: discord.Message = None
    ) -> dict:
        channels = {}

        for channel in guild.channels:
            if log_message is not None:
                await log_and_send(
                    f"Scraping metadata of channel {channel.mention} ({channel.id} in {guild.name} ({guild.id})",
                    self.bot.logger,
                    log_message,
                )

            async def check(name, value):
                if isinstance(value, list) and all(isinstance(item, discord.Member) for item in value):
                    return [member.id for member in value]
                if (
                    isinstance(value, dict)
                    and all(isinstance(item, (discord.Role, discord.Member)) for item in value.keys())
                    and all(isinstance(item, discord.PermissionOverwrite) for item in value.values())
                ):
                    return_value = {key.id: await get_object_atrs(value) for key, value in value.items()}
                    return return_value

                if isinstance(value, list) and all(
                    isinstance(item, (discord.Role, discord.abc.GuildChannel, discord.abc.Messageable))
                    for item in value
                ):
                    return [i.id for i in value]
                return None if isinstance(value, discord.Message) else None

            atrs = await get_object_atrs(channel, check=check)
            if (
                message_limit > 0
                and isinstance(channel, discord.abc.Messageable)
                and isinstance(channel, discord.abc.GuildChannel)
            ):
                if log_message is not None:
                    await log_and_send(
                        f"Scraping messages in channel {channel.mention} ({channel.id}) in {guild.name} ({guild.id})",
                        self.bot.logger,
                        log_message,
                    )
                atrs["messages"] = await get_messages(channel, message_limit=message_limit)

            channels[channel.id] = atrs

        return channels

    @commands.command()
    @commands.is_owner()
    async def scrape(self, ctx: commands.Context, limit: int = None):
        msg = await log_and_send(
            f"Scraping general metadata of {ctx.guild.name} ({ctx.guild.id})", self.bot.logger, ctx
        )

        guild_path = Path(f"scraped guilds/{ctx.guild.name}")

        guild_dict = await get_object_atrs(ctx.guild)
        guild_dict["premium_subscribers"] = [member.id for member in ctx.guild.premium_subscribers]
        guild_dict["scheduled_events"] = [await get_object_atrs(i) for i in ctx.guild.scheduled_events]
        guild_dict["stage_instances"] = [await get_object_atrs(i) for i in ctx.guild.stage_instances]

        await log_and_send(f"Scraping emojis from {ctx.guild.name} ({ctx.guild.id})", self.bot.logger, msg)
        guild_dict["emojis"] = await get_emojis(ctx.guild)

        await log_and_send(f"Scraping stickers from {ctx.guild.name} ({ctx.guild.id})", self.bot.logger, msg)
        guild_dict["stickers"] = await get_stickers(ctx.guild)

        await log_and_send(f"Scraping members in {ctx.guild.name} ({ctx.guild.id})", self.bot.logger, msg)
        guild_dict["members"] = await get_members(ctx.guild)

        await log_and_send(f"Scraping roles in {ctx.guild.name} ({ctx.guild.id})", self.bot.logger, msg)
        guild_dict["roles"] = await get_roles(ctx.guild)

        guild_dict["channels"] = await self.get_channels(ctx.guild, message_limit=limit, log_message=msg)

        await log_and_send(f"Finished scraping {ctx.guild.name} ({ctx.guild.id}), saving...", self.bot.logger, msg)

        print(json.dumps(guild_dict["channels"][796492337789403156], indent=4))
        guild_dir = Path("scraped guilds/")
        guild_dir.mkdir(exist_ok=True)
        file_name = "".join(char for char in ctx.guild.name if char.isalnum() or char in "-_ .") + ".json"

        with open(guild_dir / file_name, "w") as f:
            json.dump(guild_dict, f)  # No indentation because the file's big enough without it

        await log_and_send(f"Finished scraping {ctx.guild.name} ({ctx.guild.id})", self.bot.logger, msg)
        await ctx.author.send("Scrape finished, here's the file!", file=discord.File(guild_dir / "help.json"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Scraping(bot))
