import discord
import asyncio
from gtts import gTTS

from discord.ext import commands 


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Joining a VC:
    @commands.command(name="VCjoin", help="Joins the user's VC")
    async def vcjoin(self, ctx):
        if ctx.author.voice is None:
            # Exiting if the user is not in a voice channel
            return await ctx.send('You need to be in a voice channel to use this command!')
        else:
            channel = ctx.author.voice.channel  # Get the sender's voice channel
            await channel.connect()  # Join the channel

    # Leaving a VC:
    @commands.command(name="VCleave", help="Leaves the VC", pass_context=True)
    async def vcleave(self, ctx):
        if ctx.author.voice is None:
            # Exiting if the user is not in a voice channel
            return await ctx.send('You need to be in a voice channel to use this command!')
        else:
            server = ctx.message.guild.voice_client  # Get the server of the sender, specific VC doesn't matter.
            await server.disconnect()  # Leave the VC

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tts(self, ctx, *, message):
        tts = gTTS(message)
        with open('assets/img/tts.mp3', 'wb') as f:
            tts.write_to_fp(f)
        if ctx.author.voice is None:
            return await ctx.send('You need to be in a voice channel to use this command!')
        else:
            channel = ctx.author.voice.channel  # Get the sender's voice channel
            voice = await channel.connect()

        server = ctx.message.guild.voice_client
        voice.play(discord.FFmpegPCMAudio('assets/img/tts.mp3'))
        while voice.is_playing():
            await asyncio.sleep(1)
        await voice.disconnect()


def setup(bot):
    bot.add_cog(Voice(bot))
