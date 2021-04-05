from assets.stuff import *
from assets.dynotags_formated import dynotags

print(f"{bcolors.OKBLUE + bcolors.BOLD}Loaded cogs:{bcolors.ENDC}")
for cog in COGS:
    bot.load_extension(f"cogs.{cog}")
    print(f"{bcolors.OKBLUE + bcolors.BOLD}│ {bcolors.OKCYAN}{cog}{bcolors.ENDC}")


@bot.event
async def on_ready():
    print(f'''{bcolors.BOLD + bcolors.OKBLUE}Connected successfully!
Logged in as {bcolors.OKCYAN}{bot.user.name}{bcolors.OKBLUE}, with the ID {bcolors.OKCYAN}{bot.user.id}{bcolors.ENDC}''')
    status = f'you. And {len(bot.guilds)} servers 👀'
    await bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.watching))
    print(f'{bcolors.BOLD + bcolors.OKBLUE}Status set to "{bcolors.OKCYAN}watching {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
    print(f"{bcolors.BOLD + bcolors.OKBLUE}───────────────────────────────────────────────────────{bcolors.ENDC}")


# ON MESSAGE -----------------------------------------------------------------------------------
@bot.event
async def on_message(ctx):
    # Detect if the bot is pinged in the message
    if ctx.author != bot.user and f"<@{bot.user.id}>" in ctx.content or f"<@!{bot.user.id}>" in ctx.content:
        await ctx.add_reaction("<:ping_gun:823948139504861225>")
    # Responds with a wave emoji if the message says hi ort similar
    hellowords = ["hello", "hi", "greetings", "howdy", "hey", "yo", "ello"]
    if ctx.content.lower() in hellowords:
        await ctx.add_reaction('👋')
    # Sends messages to log channel
    if debug == "True" and ctx.author.id != 818919767784161293:
        print(f"[-] {bcolors.BOLD}DEBUG: {ctx.author}{bcolors.ENDC} {ctx.content}".replace('\n', '\n │  '))
        await bot.get_channel(826426599502381056).send(
            f"[-] DEBUG: {ctx.author.mention}\n```{ctx.content}```")

    # BANNED WORDS
    with open('assets/BadWords.txt', 'r') as f:
        badwords = f.read().split()
        for word in badwords:
            if word in ctx.content:
                await ctx.delete()
                await ctx.channel.send("Don't say that :(")

    await bot.process_commands(ctx) # Processes the commands


# ERROR HANDLING -----------------------------------------------------------------------------------
@bot.event
async def on_command_error(ctx, error):
    # If the command does not exist/is not found.
    if isinstance(error, CommandNotFound):
        await ctx.message.add_reaction("❓")
    # If the command is on cooldown.
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=discord.Embed(title=f"Slow down!", description=f"Try again in {error.retry_after:.2f}s.", color=0xeb4034))
    else:  # If its a actual error.
        try:
            embed = discord.Embed(colour=0xff0000, timestamp=ctx.message.created_at, title="**An error occurred!** Please notify Fripe if necessary.")
            embed.add_field(name="Error:", value=f"```{error}```")
            embed.set_footer(text=f"Caused by {ctx.author}")
            await ctx.send(embed=embed)  # Send error in chat
        except Exception:  # Print error to console
            print(f"{bcolors.WARNING}[X] {bcolors.BOLD}ERROR: {bcolors.ENDC + bcolors.WARNING} {error}{bcolors.ENDC}".replace('\n', '\n │  '))
        finally:  # When big oops happens
            print(f"{bcolors.FAIL}[X] {bcolors.BOLD}ERROR: {bcolors.ENDC + bcolors.FAIL} {error}{bcolors.ENDC}".replace('\n', '\n │  '))


# COMMANDS -----------------------------------------------------------------------------------
# Command to get the bots ping
@bot.command(help="Displays the bots ping")
async def ping(ctx, real=None):
    await ctx.message.add_reaction("🏓")
    if real != "fake":
        bot_ping = round(bot.latency * 1000)
    else:
        bot_ping = round(bot.latency * 9999999)
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


@bot.command(help="Gives soup")
async def soup(ctx):
    await ctx.reply("Here's your soup! <:soup:823158453022228520>")

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
        #await ctx.send(dynotags.keys())


# Prints all the minecraft discord dyno tags
@bot.command(help="Prints all tags")
@has_permissions(administrator=True)
async def alltags(ctx):
    print("Printing all tags")
    for key in dynotags.keys():
        embed = discord.Embed(colour=0x2c7bd2, title=f"?t {key}", description=dynotags[key])
        await ctx.send(embed=embed)


@bot.command(aliases=['Say'], help="Makes the bot say things")
async def echo(ctx, *, tell):
    if ctx.author.id in trusted:
        if isinstance(ctx.channel, discord.channel.DMChannel):
            print(f'{bcolors.BOLD + bcolors.WARNING}{ctx.author}{bcolors.ENDC + bcolors.FAIL} Tried to make me say: "{bcolors.WARNING + bcolors.BOLD}{tell}{bcolors.ENDC + bcolors.FAIL}" In a dm{bcolors.ENDC}')
            await ctx.send("That command isn't available in dms")
        else:
            print(f'{bcolors.BOLD + bcolors.OKCYAN}{ctx.author}{bcolors.ENDC} Made me say: "{bcolors.OKBLUE + bcolors.BOLD}{tell}{bcolors.ENDC}"')
            await ctx.message.delete()
            await ctx.send(tell)
    else:
        print(f'{bcolors.BOLD}{bcolors.WARNING}{ctx.author}{bcolors.ENDC}{bcolors.FAIL} Tried to make me say: "{bcolors.WARNING}{bcolors.BOLD}{tell}{bcolors.ENDC}{bcolors.FAIL}" But '"wasnt"f' allowed to{bcolors.ENDC}')
        await ctx.message.add_reaction("🔐")


@bot.command(aliases=['Exec'], help="Executes code")
async def execute(ctx, *, arg):
#    if ctx.author.id in trusted:
    if ctx.author.id == ownerid:  # Checking if the person is the owner
        print(f"{bcolors.OKGREEN}[EXEC] Trying to run code: {bcolors.OKCYAN}{arg}{bcolors.ENDC}".replace('\n', '\n │  '))
        try:
            exec(arg)
            await ctx.message.add_reaction("<:yes:823202605123502100>")
        except Exception as error:
            print(f"{bcolors.FAIL}[EXEC] {bcolors.BOLD}ERROR DURING EXECUTION: {bcolors.ENDC + bcolors.FAIL} {error}{bcolors.ENDC}".replace('\n', '\n │  '))
            await ctx.send(f"An error occurred during execution```\n{error}\n```")
            await ctx.message.add_reaction("<:no:823202604665929779>")
    else:
        print(f"{bcolors.OKBLUE}[EXEC] Tried to run: {bcolors.OKCYAN}{arg}{bcolors.ENDC}".replace('\n', f'\n {bcolors.OKGREEN}│{bcolors.OKCYAN}  '))
        await ctx.message.add_reaction("🔐")


@bot.command(aliases=['Eval'], help="Evaluates things")
async def evaluate(ctx, *, arg=None):
    if ctx.author.id in trusted:
        if arg != None:
            print(f"{bcolors.OKGREEN}[EVAL] Trying to evaluate: {bcolors.OKCYAN}{arg}{bcolors.ENDC}".replace('\n', '\n │  '))
            if not os.getenv('TOKEN') in eval(arg):
                try:
                    await ctx.send(eval(arg))
                    await ctx.message.add_reaction("<:yes:823202605123502100>")
                except Exception as error:
                    print(f"{bcolors.FAIL}[EVAL] {bcolors.BOLD}ERROR DURING EVALUATION: {bcolors.ENDC + bcolors.FAIL} {error}{bcolors.ENDC}".replace('\n', '\n │  '))
                    await ctx.send(f"An error occurred during evaluation```\n{error}\n```")
                    await ctx.message.add_reaction("<:no:823202604665929779>")
            else:
                await ctx.reply(''.join(random.choices(string.ascii_letters + string.digits, k=59)))
        else:
            await ctx.reply("I cant evaluate nothing")
    else:
        print(f"{bcolors.OKBLUE}[EVAL] Tried to evaluate: {bcolors.OKCYAN}{arg}{bcolors.ENDC}".replace('\n',
                                                                                                    f'\n {bcolors.OKGREEN}│{bcolors.OKCYAN}  '))
        await ctx.message.add_reaction("🔐")


# Code stolen (with consent) from "! Thonk##2761" on discord
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


@bot.command(aliases=['fripemail'], help="Sends a message to fripe")
@commands.cooldown(1, 150, commands.BucketType.user)
async def mailfripe(ctx, *, arg):
    if arg == "None":
        await ctx.send("You have to specify a message!")
    else:
        await ctx.send("Messaged Fripe!")
        await bot.get_channel(823989070845444106).send(f'{ctx.author.mention}\n- {arg}')


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



# VC COMMANDS -----------------------------------------------------------------------------------
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

# RUN THE BOT -----------------------------------------------------------------------------------
load_dotenv()
bot.run(os.getenv('TOKEN'))