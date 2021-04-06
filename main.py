from assets.stuff import *


@bot.event
async def on_ready():
    print(f'''{bcolors.BOLD + bcolors.OKBLUE}Connected successfully!
Logged in as {bcolors.OKCYAN}{bot.user.name}{bcolors.OKBLUE}, with the ID {bcolors.OKCYAN}{bot.user.id}{bcolors.ENDC}''')
    status = f'you. And {len(bot.guilds)} servers 👀'
    await bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.watching))
    print(f'{bcolors.BOLD + bcolors.OKBLUE}Status set to "{bcolors.OKCYAN}watching {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
    print(f"{bcolors.OKBLUE + bcolors.BOLD}Cogs:{bcolors.ENDC}")
    for cog in COGS:
        bot.load_extension(f"cogs.{cog}")
        print(f"{bcolors.OKBLUE + bcolors.BOLD}│ {bcolors.OKCYAN}{cog}{bcolors.ENDC}")
    print(f"{bcolors.BOLD + bcolors.OKBLUE}└───────────────────────────────────────────────────────{bcolors.ENDC}")


# ON MESSAGE -----------------------------------------------------------------------------------
@bot.event
async def on_message(ctx):
    # Detect if the bot is pinged in the message
    if ctx.author != bot.user and f"<@{bot.user.id}>" in ctx.content or f"<@!{bot.user.id}>" in ctx.content:
        await ctx.add_reaction("<:ping_gun:823948139504861225>")
    # Responds with a wave emoji if the message says hi ort similar
    hellowords = ["hello", "hi", "greetings", "howdy", "hey", "yo", "ello", "hallo", "hej", "tjena", "sup", "wassup", "god dag", "hallå", "holla"]
    if ctx.content.lower() in hellowords:
        await ctx.add_reaction('<a:wave_animated:826546112374243353>')
    # Sends messages to log channel
    if debug == "True" and ctx.author.id != 818919767784161293:
        print(f"[-] {bcolors.BOLD}DEBUG: {ctx.author}{bcolors.ENDC} {ctx.content}".replace('\n', '\n │  '))
        await bot.get_channel(826426599502381056).send(f"[-] DEBUG: {ctx.author.mention}\n```{ctx.content}```")

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
            print(f"{bcolors.WARNING}[X] {bcolors.BOLD}ERROR: {bcolors.ENDC + bcolors.WARNING} {error}{bcolors.ENDC}".replace('\n', '\n │ '))
        finally:  # When big oops happens
            print(f"{bcolors.FAIL}[X] {bcolors.BOLD}ERROR: {bcolors.ENDC + bcolors.FAIL} {error}{bcolors.ENDC}".replace('\n', '\n │ '))


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


@bot.command(help="Flips a coin!")
async def coinflip(ctx):
    await ctx.reply(random.choice(["Heads!", "Tails!"]))


@bot.command(help="A magic eightball")
async def eightball(ctx):
    await ctx.reply(random.choice(["Yes", "No", "<:perhaps:819028239275655169>", "Surely", "Maybe tomorrow", "Idk ¯\_(ツ)_/¯"]))


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

# RUN THE BOT -----------------------------------------------------------------------------------
load_dotenv()
bot.run(os.getenv('TOKEN'))