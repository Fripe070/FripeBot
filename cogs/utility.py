from assets.stuff import *


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @bot.command(help="Shows this page")
        async def help(ctx):
            commandlist = ''
            for command in self.bot.walk_commands():
                commandlist += f'**{command}** - {command.help}\n'
            embed = discord.Embed(colour=ctx.author.colour, timestamp=ctx.message.created_at, title=f"Help",
                                  description=f"**{bot.user.name}**, a bot created by <@444800636681453568> when he was bored!")
            embed.add_field(name="Commands", value=commandlist)
            embed.set_footer(text=f"Requested by {ctx.author}")
            await ctx.reply(embed=embed)

        # Command to get info about the minecraft discord dyno tags
        @bot.command(aliases=['dynotags', 'dt'], help="Tags for dyno in maincord")
        async def dynotag(ctx, tagname=None, extra=None):
            if tagname != None:
                if extra != None and extra.lower() == "dyno" or "d":
                    await ctx.message.delete()
                    await ctx.send(dynotags[tagname])
                else:
                    try:
                        embed = discord.Embed(colour=0x00ffff, timestamp=ctx.message.created_at)
                        embed.set_footer(text=f"Requested by {ctx.author}")
                        embed.add_field(name="Tag content:", value=dynotags[tagname])
                        embed.add_field(name="Raw tag data:", value=f"```{dynotags[tagname]}```")
                        await ctx.reply(embed=embed)
                    except KeyError:
                        await ctx.reply("That's not a valid tag!")
            else:
                embed = discord.Embed(colour=0x00ffff, title="Dyno tags", timestamp=ctx.message.created_at)
                embed.set_footer(text=f"Requested by {ctx.author}")
                embed.add_field(name="Tags:", value=", ".join(k for k in dynotags.keys()))
                await ctx.reply(embed=embed)
                # await ctx.send(dynotags.keys())

        # Prints all the minecraft discord dyno tags
        @bot.command(help="Prints all tags (admin only)")
        @has_permissions(administrator=True)
        async def alltags(ctx):
            print(f'{bcolors.OKGREEN}Printing all tags in channel: {bcolors.OKCYAN}#{ctx.channel}{bcolors.OKGREEN} ID:"{bcolors.OKCYAN}{ctx.channel.id}{bcolors.OKGREEN}"{bcolors.ENDC}')
            for key in dynotags.keys():
                embed = discord.Embed(colour=0x2c7bd2, title=f"?t {key}", description=dynotags[key])
                await ctx.send(embed=embed)

        # Command to get info about a account
        @bot.command(help="Displays information about a discord user")
        async def whois(ctx, member: discord.Member = None):
            if not member:
                member = ctx.message.author
            roles = [role.mention for role in member.roles[1:]]
            roles.reverse()

            def afunctionthatfroopwants(text):
                e = list(text)
                bruh = []
                for lol in e:
                    if lol == "`":
                        bruh.append("\`")
                    else:
                        bruh.append(lol)
                return "".join(bruh)

            embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at,
                                  title=f"User Info - {member}")
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"Requested by {ctx.author}")

            embed.add_field(name=f"Info about {member.name}", value=f"""**Username:** {afunctionthatfroopwants(member.name)}
            **Nickname:** {afunctionthatfroopwants(member.display_name)}
            **Mention:** {member.mention}
            **ID:** {member.id}
            **Account Created At:** {member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")}
            **Activity:** {afunctionthatfroopwants(member.activity.name)}
            **Joined server at:** {member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")}
            **Is user on mobile:** {member.is_on_mobile()}
            **Highest Role:** {member.top_role.mention}

            **Roles:** {" ".join(roles)}""")

            await ctx.send(embed=embed)

        @bot.command()
        async def allroles(ctx):
            embed = discord.Embed(colour=0x2c7bd2, title="e", description=f"")
            await ctx.send(embed=embed)

        @bot.command(aliases=['Exec'], help="Executes code")
        async def execute(ctx, *, arg):
            #    if ctx.author.id in trusted:
            if ctx.author.id == ownerid:  # Checking if the person is the owner
                try:
                    exec(arg)
                    await ctx.message.add_reaction("<:yes:823202605123502100>")
                except Exception:
                    await ctx.message.add_reaction("<:no:823202604665929779>")
            else:
                await ctx.message.add_reaction("🔐")

        @bot.command(aliases=['Eval'], help="Evaluates things")
        async def evaluate(ctx, *, arg=None):
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
                    except Exception:
                        await ctx.message.add_reaction("<:no:823202604665929779>")
            else:
                await ctx.message.add_reaction("🔐")

        @bot.command(help="Counts the amount of people in the server (can have bots/all specified at the end)")
        async def members(ctx):
            embed = discord.Embed(colour=ctx.author.colour, timestamp=ctx.message.created_at, title="Member Info")
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            embed.add_field(name=f"Users:", value=f"{len([member for member in ctx.guild.members if not member.bot])}")
            embed.add_field(name=f"Bots:", value=f"{len([member for member in ctx.guild.members if member.bot])}")
            embed.add_field(name=f"Total:", value=f"{len(ctx.guild.members)}")
            await ctx.reply(embed=embed)

        @bot.command(aliases=['fripemail'], help="Sends a message to fripe")
        @commands.cooldown(1, 150, commands.BucketType.user)
        async def mailfripe(ctx, *, arg):
            if arg == "None":
                await ctx.send("You have to specify a message!")
            else:
                await ctx.send("Messaged Fripe!")
                await bot.get_channel(823989070845444106).send(f'{ctx.author.mention}\n- {arg}')

        # Command to get the bots ping
        @bot.command(help="Displays the bots ping")
        async def ping(ctx, real=None):
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

        @bot.command(help="Scrambles the text supplied")
        async def scramble(ctx, *, arg):
            await ctx.reply(''.join(random.sample(arg, len(arg))))

        # Code stolen (with consent) from "! Thonk##2761" on discord
        # Code is heavily modified by me
        @bot.command(aliases=['source'], help="Links my GitHub profile")
        async def github(ctx, member: discord.Member = None):
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

        @bot.command(aliases=['Say'], help="Makes the bot say things")
        async def echo(ctx, *, tell):
            if ctx.author.id in trusted:
                if isinstance(ctx.channel, discord.channel.DMChannel):
                    print(
                        f'{bcolors.BOLD + bcolors.WARNING}{ctx.author}{bcolors.ENDC + bcolors.FAIL} Tried to make me say: "{bcolors.WARNING + bcolors.BOLD}{tell}{bcolors.ENDC + bcolors.FAIL}" In a dm{bcolors.ENDC}')
                    await ctx.send("That command isn't available in dms")
                else:
                    print(
                        f'{bcolors.BOLD + bcolors.OKCYAN}{ctx.author}{bcolors.ENDC} Made me say: "{bcolors.OKBLUE + bcolors.BOLD}{tell}{bcolors.ENDC}"')
                    await ctx.message.delete()
                    await ctx.send(tell)
            else:
                print(
                    f'{bcolors.BOLD}{bcolors.WARNING}{ctx.author}{bcolors.ENDC}{bcolors.FAIL} Tried to make me say: "{bcolors.WARNING}{bcolors.BOLD}{tell}{bcolors.ENDC}{bcolors.FAIL}" But '"wasnt"f' allowed to{bcolors.ENDC}')
                await ctx.message.add_reaction("🔐")


def setup(bot):
    bot.add_cog(Utility(bot))