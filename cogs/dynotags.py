import discord
import requests
from discord.ext import commands


class Dynotags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["dynotags", "dt"])
    async def dynotag(self, ctx: commands.Context, tagname=None, *, raw_args=None):
        url = "https://raw.githubusercontent.com/minecraftdiscordsupportpeeps/dyno-tags/master/tags.json"
        tags = requests.get(url).json()

        if not tagname or tagname not in tags:
            embed = discord.Embed(
                title="Dyno Tags:",
                description=", ".join(sorted(tags.keys())),
                color=0x2473C7,
            )
            await ctx.reply(embed=embed)
            return

        if raw_args:
            args = raw_args.split(" ")
            if "-e" in args or "--embed" in args:
                embed = discord.Embed(title=f'Tag "{tagname}" content:')
                embed.add_field(name="**Plaintext:**", value=tags[tagname])
                embed.add_field(name="**Raw:**", value=f"```\n{tags[tagname]}```")
                await ctx.reply(embed=embed)
                return

        await ctx.send(tags[tagname])
        await ctx.message.delete()

    @commands.command(aliases=["dtlist"])
    @commands.is_owner()
    async def alltags(self, ctx: commands.Context, channel: discord.TextChannel = None):
        if not channel:
            await ctx.reply("Please specify a channel.")
            return

        url = "https://raw.githubusercontent.com/minecraftdiscordsupportpeeps/dyno-tags/master/tags.json"
        tags = requests.get(url).json()

        await ctx.reply(f"Purging and sending list of tags to {channel.mention}")
        await channel.purge(limit=None)
        for tag in tags:
            embed = discord.Embed(title=f"?t {tag}", description=tags[tag], color=0x2473C7)
            await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Dynotags(bot))
