from assets.stuff import *


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Joining a VC:
        @bot.command(name="VCjoin", help="Joins the user's VC")
        async def vcjoin(ctx):
            if ctx.author.voice is None:
                # Exiting if the user is not in a voice channel
                return await ctx.send('You need to be in a voice channel to use this command!')
            else:
                channel = ctx.author.voice.channel  # Get the sender's voice channel
                await channel.connect()  # Join the channel

        # Leaving a VC:
        @bot.command(name="VCleave", help="Leaves the VC", pass_context=True)
        async def vcleave(ctx):
            if ctx.author.voice is None:
                # Exiting if the user is not in a voice channel
                return await ctx.send('You need to be in a voice channel to use this command!')
            else:
                server = ctx.message.guild.voice_client  # Get the server of the sender, specific VC doesn't matter.
                await server.disconnect()  # Leave the VC

def setup(bot):
    bot.add_cog(Voice(bot))