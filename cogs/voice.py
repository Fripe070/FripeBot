import discord
import asyncio

from discord.ext import commands


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.paused = False
        self.loop = False

    @commands.command(aliases=['vcjoin'])
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send('You need to be in a voice channel to use this command!')
        else:
            channel = ctx.author.voice.channel  # Get the sender's voice channel
            await channel.connect()  # Join the channel

    @commands.command(aliases=['vcleave'])
    async def leave(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send('You need to be in a voice channel to use this command!')
        else:
            server = ctx.message.guild.voice_client  # Get the server of the sender, specific VC doesn't matter.
            await server.disconnect()  # Leave the VC

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tts(self, ctx, *, message):
        if ctx.author.voice is None:
            return await ctx.send('You need to be in a voice channel to use this command!')
        else:
            channel = ctx.author.voice.channel  # Get the sender's voice channel
            voice = await channel.connect()

        voice.play(discord.FFmpegPCMAudio(
            f'http://translate.google.com/translate_tts?total=1&idx=0&textlen=32&client=tw-ob&q={message}&tl=En-gb'
        ))
        while voice.is_playing():
            await asyncio.sleep(1)
        await voice.disconnect()

    @commands.command()
    async def play(self, ctx, *, url=None):
        if ctx.author.voice is None:
            return await ctx.send('You need to be in a voice channel to use this command!')
        channel = ctx.author.voice.channel
        try:
            voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            await voice.move_to(channel)
        except AttributeError:
            voice = await channel.connect()

        if url:
            self.queue.append(url)
        for attachment in ctx.message.attachments:
            self.queue.append(attachment.url)

        voice.play(discord.FFmpegPCMAudio(url))

        while voice.is_playing():
            await asyncio.sleep(1)
        await voice.disconnect()

    @commands.command()
    async def nowplaying(self, ctx):
        if self.queue:
            await ctx.reply(f'Now playing: {self.queue[0]}')
        else:
            return await ctx.send('There is nothing playing!')

    # I'll get this working sometime else
    # @commands.command()
    # async def queue(self, ctx):
    #     if self.queue:
    #         embed = discord.Embed(
    #             title="Queue",
    #             description=", ".join(f"[{i + 1}]({song}) - {song}" for i, song in enumerate(self.queue)),
    #         )
    #
    #         await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Voice(bot))
