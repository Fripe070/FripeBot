import json
import os
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Optional, Union

import discord
from discord import Object, utils
from discord.abc import Snowflake
from discord.ext import commands
from discord.object import OLDEST_OBJECT


# This is cursed. I wish I could do this differently. If you know how to make this not terrible, PLEASE contact me
async def raw_history(
    self,
    *,
    limit: Optional[int] = 100,
    before: Optional[Union["Snowflake", datetime]] = None,
    after: Optional[Union["Snowflake", datetime]] = None,
    around: Optional[Union["Snowflake", datetime]] = None,
    oldest_first: Optional[bool] = None,
) -> AsyncIterator[dict]:
    """Returns an :term:`asynchronous iterator` that enables receiving the destination's message history.

    You must have :attr:`~discord.Permissions.read_message_history` permissions to use this.

    Examples
    ---------

    Usage ::

        counter = 0
        async for message in channel.history(limit=200):
            if message.author == client.user:
                counter += 1

    Flattening into a list: ::

        messages = [message async for message in channel.history(limit=123)]
        # messages is now a list of Message...

    All parameters are optional.

    Parameters
    -----------
    limit: Optional[:class:`int`]
        The number of messages to retrieve.
        If ``None``, retrieves every message in the channel. Note, however,
        that this would make it a slow operation.
    before: Optional[Union[:class:`~discord.abc.Snowflake`, :class:`datetime.datetime`]]
        Retrieve messages before this date or message.
        If a datetime is provided, it is recommended to use a UTC aware datetime.
        If the datetime is naive, it is assumed to be local time.
    after: Optional[Union[:class:`~discord.abc.Snowflake`, :class:`datetime.datetime`]]
        Retrieve messages after this date or message.
        If a datetime is provided, it is recommended to use a UTC aware datetime.
        If the datetime is naive, it is assumed to be local time.
    around: Optional[Union[:class:`~discord.abc.Snowflake`, :class:`datetime.datetime`]]
        Retrieve messages around this date or message.
        If a datetime is provided, it is recommended to use a UTC aware datetime.
        If the datetime is naive, it is assumed to be local time.
        When using this argument, the maximum limit is 101. Note that if the limit is an
        even number then this will return at most limit + 1 messages.
    oldest_first: Optional[:class:`bool`]
        If set to ``True``, return messages in oldest->newest order. Defaults to ``True`` if
        ``after`` is specified, otherwise ``False``.

    Raises
    ------
    ~discord.Forbidden
        You do not have permissions to get channel message history.
    ~discord.HTTPException
        The request to get message history failed.

    Yields
    -------
    :class:`~discord.Message`
        The message with the message data parsed.
    """

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

    if oldest_first is None:
        reverse = after is not None
    else:
        reverse = oldest_first

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


def ensuredir(path: Path):
    os.makedirs(path, exist_ok=True)


class Scraping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def scrape(self, ctx: commands.Context, limit: int = None):
        self.bot.logger.info(f"Scraping the content of {ctx.guild.name} ({ctx.guild.id})")
        scrape_msg = await ctx.send("Scraping guild!")
        guildpath = Path(f"scraped guilds/{ctx.guild.name}")
        ensuredir(guildpath)

        for channel in ctx.guild.channels:
            if isinstance(channel, discord.CategoryChannel):
                continue
            perms = channel.permissions_for(ctx.guild.me)
            if not perms.read_messages or not perms.read_message_history:
                continue

            await scrape_msg.edit(content=f"Scraping: {channel.mention} ({channel.name})")

            channelpath = guildpath
            if channel.category:
                channelpath = channelpath / str(channel.category.name)
                ensuredir(channelpath)
            channelpath = channelpath / str(channel.name)

            self.bot.logger.info(f"Started scraping {channel.name}.")
            messages = []
            try:
                # noinspection PyUnresolvedReferences
                async for message in channel.raw_history(limit=limit):
                    messages.append(message)
            except discord.errors.Forbidden:
                continue

            with open(f"{channelpath}.json", "w") as f:
                json.dump(messages, f, indent=4)

            self.bot.logger.info(f"Finished scraping {channel.name}.")

        self.bot.logger.info(f"Finished scraping the content of {ctx.guild.name} ({ctx.guild.id})")
        await scrape_msg.edit(content="Finished scraping channels.")
        await scrape_msg.reply(f"{ctx.author.mention}")


async def setup(bot):
    await bot.add_cog(Scraping(bot))
