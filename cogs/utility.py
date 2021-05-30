from assets.stuff import *


class Utility(Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to get info about the minecraft discord dyno tags
    @command(aliases=['dynotags', 'dt'], help="Tags for dyno in maincord. Syntax f!dt [tagname] {raw/d/dyno}")
    async def dynotag(self, ctx, tagname=None, extra=None):
        if tagname != None:
            if extra != None:
                if extra.lower() == "dyno" or extra.lower() == "d" or extra.lower() == "raw":
                    await ctx.message.delete()
                    await ctx.send(dynotags[tagname])
            elif tagname in dynotags:
                try:
                    embed = discord.Embed(colour=0x00ffff, timestamp=ctx.message.created_at)
                    embed.set_footer(text=f"Requested by {ctx.author}")
                    embed.add_field(name="Tag content:", value=dynotags[tagname])
                    embed.add_field(name="Raw tag data:", value=f"```{dynotags[tagname]}```")
                    await ctx.reply(embed=embed)
                except KeyError:
                    await ctx.reply("That's not a valid tag!")
            else:
                await ctx.reply("That does not exist")
        else:
            embed = discord.Embed(colour=0x00ffff, title="Dyno tags", timestamp=ctx.message.created_at)
            embed.set_footer(text=f"Requested by {ctx.author}")
            embed.add_field(name="Tags:", value=", ".join(k for k in dynotags.keys()))
            await ctx.reply(embed=embed)
            # await ctx.send(dynotags.keys())

    # Prints all the minecraft discord dyno tags
    @command(help="Prints all tags (admin only)")
    async def alltags(self, ctx, channel: discord.TextChannel):
        if ctx.author.id in trusted or ctx.author.server_premission.administrator:
            await channel.purge(limit=200)
            print(
                f'{bcolors.OKGREEN}Printing all tags in channel: {bcolors.OKCYAN}#{channel}{bcolors.OKGREEN} ID:"{bcolors.OKCYAN}{channel.id}{bcolors.OKGREEN}"{bcolors.ENDC}')
            for key in dtags.keys():
                embed = discord.Embed(colour=0x2c7bd2, title=key, description=dtags[key])
                await channel.send(embed=embed)
        else:
            ctx.reply("You don't have the required permissions to perform this command! :pensive:")

    @command(help="Gets all tags")
    async def updatetags(self, ctx, channel: discord.TextChannel):
        if ctx.author.id in trusted or ctx.author.server_premission.administrator:
            message = await ctx.reply("Updating all tags (this might take some time)")
            channel = bot.get_channel(channel.id)
            tags = {}
            some_list = []

            async for e in channel.history(limit=200):
                some_list.append(e.content)

            some_list.reverse()  # Reverses the list

            for index in range(0, len(some_list), 2):
                tags[some_list[index]] = some_list[index + 1]

                with open('assets/dynotags.json', 'w') as f:
                    json.dump(tags, f, indent=4)
            await message.edit(content="Updated all the tags!")
        else:
            ctx.reply("You don't have the required permissions to perform this command! :pensive:")

    @command(aliases=["pfpget", "gpfp", "pfp"], help="Gets a users profile picture at a high resolution")
    async def getpfp(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.message.author
        pfp = str(member.avatar_url)[:-4] + "4096"
        embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at,
                              title=f"{member.display_name}'s pfp")
        embed.set_image(url=pfp)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    # Command to get info about a account
    @command(help="Displays information about a discord user")
    async def whois(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.message.author
        roles = [role.mention for role in member.roles[1:]]
        roles.reverse()
        pfp = str(member.avatar_url)[:-4] + "4096"

        embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at,
                              title=f"User Info - {member}")
        embed.set_thumbnail(url=pfp)
        embed.set_footer(text=f"Requested by {ctx.author}")

        embed.add_field(name=f"Info about {member.name}", value=f"""**Username:** {rembackslash(member.name)}
        **Nickname:** {rembackslash(member.display_name)}
        **Mention:** {member.mention}
        **ID:** {member.id}
        **Account Created At:** {member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")}
        **Joined server at:** {member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")}
        **Is user on mobile:** {member.is_on_mobile()}
        **Highest Role:** {member.top_role.mention}

        **Roles:** {" ".join(roles)}""")
#            **Activity:** {afunctionthatfroopwants(member.activity.name)}
        await ctx.send(embed=embed)

    @command()
    async def allroles(self, ctx):
        embed = discord.Embed(colour=0x2c7bd2, title="e", description=f"")
        await ctx.send(embed=embed)

    @command(aliases=['Exec'], help="Executes code")
    async def execute(self, ctx, *, code):
        #    if ctx.author.id in trusted:
        if ctx.author.id == ownerid:  # Checking if the person is the owner
            code = code.replace('```py', '').replace('```', '').strip()
            code = '\n'.join([f'\t{line}' for line in code.splitlines()])
            function_code = (
                'async def exec_code(self, ctx):\n'
                f'{code}')
            try:
                exec(function_code)
                await locals()['exec_code'](self, ctx)
                await ctx.message.add_reaction("<:yes:823202605123502100>")
            except Exception as error:
                await ctx.message.add_reaction("<:no:823202604665929779>")
                await ctx.reply(embed=discord.Embed(colour=0xff0000,
                                                    timestamp=ctx.message.created_at,
                                                    title="Your code failed to run!",
                                                    description=f"```{error}```"))
        else:
            await ctx.message.add_reaction("🔐")

    @command(aliases=['Eval'], help="Evaluates things")
    async def evaluate(self, ctx, *, arg=None):
        if arg is None:
            await ctx.reply("I cant evaluate nothing")
            return
        if ctx.author.id in trusted:  # Checks if the user is trusted
            # Checks if the bots token is in the output
            if os.getenv('TOKEN') in str(eval(arg)):
                # Sends a randomly generated string that looks like a token
                await ctx.reply(''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-_", k=59)))
            else:
                try:
                    await ctx.reply(eval(arg))  # Actually Evaluates
                    await ctx.message.add_reaction("<:yes:823202605123502100>")
                except Exception as error:
                    await ctx.message.add_reaction("<:no:823202604665929779>")
                    await senderror(ctx, Exception)
        else:
            await ctx.message.add_reaction("🔐")

    @command(help="Counts the amount of people in the server (can have bots/all specified at the end)")
    async def members(self, ctx):
        embed = discord.Embed(colour=ctx.author.colour, timestamp=ctx.message.created_at, title="Member Info")
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        embed.add_field(name=f"Users:", value=f"{len([member for member in ctx.guild.members if not member.bot])}")
        embed.add_field(name=f"Bots:", value=f"{len([member for member in ctx.guild.members if member.bot])}")
        embed.add_field(name=f"Total:", value=f"{len(ctx.guild.members)}")
        await ctx.reply(embed=embed)

    @command(aliases=['fripemail'], help="Sends a message to fripe")
    @commands.cooldown(1, 150, commands.BucketType.user)
    async def mailfripe(self, ctx, *, arg):
        if arg == "None":
            await ctx.send("You have to specify a message!")
        else:
            await ctx.message.delete()
            await ctx.send("Messaged Fripe!")
            await bot.get_channel(823989070845444106).send(f'{ctx.author.mention}\n- {arg}')

    # Command to get the bots ping
    @command(help="Displays the bots ping")
    async def ping(self, ctx, real=None):
        await ctx.message.add_reaction("🏓")
        bot_ping = round(bot.latency * 1000)
        if bot_ping < 130:
            color = 0x44ff44
        elif bot_ping > 130 and bot_ping < 180:
            color = 0xff8c00
        else:
            color = 0xff2200
        embed = discord.Embed(title="Pong! :ping_pong:",
                              description=f"The ping is **{bot_ping}ms!**",
                              color=color)
        await ctx.reply(embed=embed)

    @command(help="Scrambles the text supplied")
    async def scramble(self, ctx, *, arg):
        await ctx.reply(''.join(random.sample(arg, len(arg))))

    # Code stolen (with consent) from "! Thonk##2761" on discord
    # Code is heavily modified by me
    @command(aliases=['source'], help="Links my GitHub profile")
    async def github(self, ctx, member: discord.Member = None):
        embed = discord.Embed(title="Fripe070", url="https://github.com/Fripe070",
                              color=0x00ffbf, timestamp=ctx.message.created_at)
        embed.set_author(name="Fripe070", url="https://github.com/Fripe070",
                         icon_url="https://github.com/TechnoShip123/DiscordBot/blob/master/resources/GitHub-Mark-Light-32px.png?raw=true")
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/fripe070")
        embed.add_field(name="This bot:", value="https://github.com/Fripe070/FripeBot")
        embed.set_footer(text="Requested by: " + ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.message.delete()
        if member != None:
            await ctx.send(f'{member.mention} Please take a look to my github', embed=embed)
        else:
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))



"""@command(help="Shows this page")
async def help(ctx, *, commandname = None):
    embed = discord.Embed(colour=ctx.author.colour, timestamp=ctx.message.created_at, title=f"Help",
                          description=f"**{bot.user.name}**, a bot created by <@444800636681453568> when he was bored!")
    embed.set_footer(text=f"Requested by {ctx.author}")
    commandlist = ''
    for command in self.bot.walk_commands():
        commandlist += f'**{command}** - {command.help}\n'
    embed.add_field(name="Commands", value=commandlist)
    await ctx.reply(embed=embed)"""