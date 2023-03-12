from datetime import datetime
from typing import Optional, Union

import discord
from discord import Colour, Member


class BetterEmbed(discord.Embed):
    def __init__(
        self,
        *,
        timestamp: Optional[datetime] = datetime.now(),
        colour: Optional[Union[int, Colour, Member]] = None,
        color: Optional[Union[int, Colour, Member]] = None,
        **kwargs
    ) -> None:
        maybe_member = colour if colour is not None else color
        if isinstance(maybe_member, Member):
            color = colour = maybe_member.color

        super().__init__(timestamp=timestamp, colour=colour, color=color, **kwargs)
