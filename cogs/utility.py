from assets.stuff import *


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            print("Printing all tags")
            for key in dynotags.keys():
                embed = discord.Embed(colour=0x2c7bd2, title=f"?t {key}", description=dynotags[key])
                await ctx.send(embed=embed)

        # Command to get info about a account
        @bot.command(help="Displays information about a discord user")
        async def whois(ctx, member: discord.Member = None):
            if not member:
                member = ctx.message.author
            roles = [role.mention for role in member.roles[1:]]
            embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at,
                                  title=f"User Info - {member}")
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"Requested by {ctx.author}")

            embed.add_field(name=f"Info about {member.name}", value=f"""**Username:** {member.name}
            **Nickname:** {member.display_name}
            **Mention:** {member.mention}
            **ID:** {member.id}
            **Account Created At:** {member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")}
            **Activity:** {member.activity.name}
            **Joined server at:** {member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")}
            **Is user on mobile:** {member.is_on_mobile()}
            **Highest Role:** {member.top_role.mention}

            **Roles:** {" ".join(roles)}""")
            await ctx.send(embed=embed)

        @bot.command(aliases=['Exec'], help="Executes code")
        async def execute(self, ctx, *, arg):
            #    if ctx.author.id in trusted:
            if ctx.author.id == ownerid:  # Checking if the person is the owner
                print(f"{bcolors.OKGREEN}[EXEC] Trying to run code: {bcolors.OKCYAN}{arg}{bcolors.ENDC}".replace('\n',
                                                                                                                 '\n │  '))
                try:
                    exec(arg)
                    await ctx.message.add_reaction("<:yes:823202605123502100>")
                except Exception as error:
                    print(
                        f"{bcolors.FAIL}[EXEC] {bcolors.BOLD}ERROR DURING EXECUTION: {bcolors.ENDC + bcolors.FAIL} {error}{bcolors.ENDC}".replace(
                            '\n', '\n │  '))
                    await ctx.send(f"An error occurred during execution```\n{error}\n```")
                    await ctx.message.add_reaction("<:no:823202604665929779>")
            else:
                print(f"{bcolors.OKBLUE}[EXEC] Tried to run: {bcolors.OKCYAN}{arg}{bcolors.ENDC}".replace('\n',
                                                                                                          f'\n {bcolors.OKGREEN}│{bcolors.OKCYAN}  '))
                await ctx.message.add_reaction("🔐")

        @bot.command(aliases=['Eval'], help="Evaluates things")
        async def evaluate(ctx, *, arg=None):
            if ctx.author.id in trusted:
                if arg is not None:
                    print(f"{bcolors.OKGREEN}[EVAL] Trying to evaluate: {bcolors.OKCYAN}{arg}{bcolors.ENDC}".replace('\n', '\n │  '))
                    if os.getenv('TOKEN') in str(eval(arg)):
                        await ctx.reply(''.join(random.choices(string.ascii_letters + string.digits, k=59)))
                    else:
                        try:
                            await ctx.send(eval(arg))
                            await ctx.message.add_reaction("<:yes:823202605123502100>")
                        except Exception as error:
                            print(f"{bcolors.FAIL}[EVAL] {bcolors.BOLD}ERROR DURING EVALUATION: {bcolors.ENDC + bcolors.FAIL}{error}{bcolors.ENDC}".replace('\n', '\n │  '))
                            await ctx.message.add_reaction("<:no:823202604665929779>")
                else:
                    await ctx.reply("I cant evaluate nothing")
            else:
                print(f"{bcolors.OKBLUE}[EVAL] Tried to evaluate: {bcolors.OKCYAN}{arg}{bcolors.ENDC}".replace('\n', f'\n {bcolors.OKGREEN}│{bcolors.OKCYAN}  '))
                await ctx.message.add_reaction("🔐")

        @bot.command(help="Counts the amount of people in the server")
        async def members(ctx, bots=None):
            if bots is None:  # Deafults to just users
                servermembers = [member for member in ctx.guild.members if not member.bot]
                await ctx.send(f"There is a total of {len(servermembers)} people in this server.")
            elif bots.lower() == "all":  # Command to count all acounts in the server
                await ctx.send(f"There is a total of {str(len(ctx.guild.members))} members in this server.")
            elif bots.lower() == "bots":  # Command to only count the bots
                servermembers = [member for member in ctx.guild.members if member.bot]
                await ctx.send(f"There is a total of {len(servermembers)} bots in this server.")
            else:  # Bad code but it works
                servermembers = [member for member in ctx.guild.members if not member.bot]
                await ctx.send(f"There is a total of {len(servermembers)} people in this server.")


def setup(bot):
    bot.add_cog(Utility(bot))