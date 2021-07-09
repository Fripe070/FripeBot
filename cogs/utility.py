from assets.stuff import *


class Utility(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(aliases=["pfpget", "gpfp", "pfp"], help="Gets a users profile picture at a high resolution")
    async def getpfp(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.message.author

        embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at,
                              title=f"{member.display_name}'s pfp")
        embed.set_image(url=getpfp(member))
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

    """
    @command()
    async def allroles(self, ctx):
        embed = discord.Embed(colour=0x2c7bd2, title="e", description=f"")
        await ctx.send(embed=embed)
    """

    @command()
    async def webget(self, ctx, site: str):
        if ctx.author.id in trusted:
            if not site.startswith("http"):
                site = "https://" + site
            output = requests.get(site).text
            num_of_fields = len(output) // 1024 + 1
            for i in range(num_of_fields):
                embed = discord.Embed(timestamp=ctx.message.created_at,
                                      title=f"Test",
                                      description=output[i * 1024:i + 1 * 1024])
                await ctx.reply(embed=embed)
        else:
            await ctx.message.add_reaction("🔐")

    @command(aliases=['Exec'], help="Executes code")
    async def execute(self, ctx, *, code):
        #    if ctx.author.id in trusted:
        if ctx.author.id == ownerid:  # Checking if the person is the owner
            if code is None:
                await ctx.reply("I cant execute nothing")
                return
            code = code.replace('```py', '').replace('```', '').strip()
            code = '\n'.join([f'\t{line}' for line in code.splitlines()])
            function_code = (
                'async def exec_code(self, ctx):\n'
                f'  {code}')
            try:
                exec(function_code)
                output = await locals()['exec_code'](self, ctx)
                if output:
                    formatted_output = '\n'.join(output) if len(code.splitlines()) > 1 else output
                    await ctx.reply(embed=discord.Embed(colour=0xff0000,
                                                        timestamp=ctx.message.created_at,
                                                        title="Your code failed ran successfully!",
                                                        description=f"```{formatted_output}```"))
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

    @command(aliases=['remfripe'], help="Sends a reminder to fripe")
    @commands.cooldown(1, 150, commands.BucketType.user)
    async def remindfripe(self, ctx, *, arg):
        if arg == "None":
            await ctx.send("You have to specify a message!")
        else:
            await ctx.send("Reminded Fripe!")
            await bot.get_channel(824022687759990845).send(f'{ctx.author.mention}\n- {arg}')

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

    @command(aliases=['def', 'definition'], help="Gets the defenition for a word")
    async def define(self, ctx, word, lang="en_GB"):
        resp = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}')
        resp = resp.json()

        try:
            resp = resp[0]["meanings"]
        except KeyError:
            embed = discord.Embed(title="Could not find a defenition for that word!",
                                  colour=ctx.author.colour,
                                  timestamp=ctx.message.created_at
                                  )
            await ctx.reply(embed=embed)
            return
        embed = discord.Embed(title=f"Defenition of the word {word}")

        for i in resp:
            for e in i["definitions"]:
                try:
                    embed.add_field(name=i["partOfSpeech"], value=f'**Defenition:** ```{e["definition"]}```\n**Example:** ```{e["example"]}```')
                except KeyError:
                    try:
                        embed.add_field(name=i["partOfSpeech"], value=f'Defenition: ```{e["definition"]}```')
                    except KeyError:
                        embed.add_field(name="e", value=f'Defenition: ```{e["definition"]}```')

        await ctx.reply(embed=embed)

    @command()
    async def allpfps(self, ctx):
        if ctx.author.id in trusted:
            print("Getting all pfps")

            today = date.today()
            made = False
            trynr = 0

            while made is False:
                try:
                    os.mkdir(f"E:\\Data\\Discord\\pfps\\{today} {trynr}")
                    made = True
                except FileExistsError:
                    trynr += 1

            for member in ctx.guild.members:
                pfp = getpfp(member)

                img_data = requests.get(pfp).content
                try:
                    with open(f"E:\\Data\\Discord\\pfps\\{today} {trynr}\\{member.name} {member.id}.png", 'wb') as f:
                        f.write(img_data)
                except Exception:
                    await ctx.send(f"Failed to downlaod the pfp of {member.name} {member.id}")

            await ctx.message.add_reaction("👍")
            await ctx.reply("Downloaded pfps")

        else:
            await ctx.message.add_reaction("🔐")


def setup(bot):
    bot.add_cog(Utility(bot))