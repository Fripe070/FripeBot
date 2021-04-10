from assets.stuff import *



reloads = []
for cog in COGS:
    try:
        bot.load_extension(f"cogs.{cog}")
        reloads.append(f"{bcolors.OKBLUE}│ {bcolors.OKGREEN}{cog}")
    except:
        reloads.append(f"{bcolors.FAIL}│ {bcolors.WARNING}{cog}")


@bot.event
async def on_ready():
    status = f'you. And {len(bot.guilds)} servers 👀'
    await bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.watching))
    print(f'''{bcolors.BOLD + bcolors.OKBLUE}Connected successfully!
Logged in as {bcolors.OKCYAN}{bot.user.name}{bcolors.OKBLUE}, with the ID {bcolors.OKCYAN}{bot.user.id}
{bcolors.OKBLUE}Status set to "{bcolors.OKCYAN}watching {status}{bcolors.OKBLUE}"
Cogs:
''' + "\n".join(reloads) + f"\n{bcolors.OKBLUE}└───────────────────────────────────────────────────────{bcolors.ENDC}")


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
    if debug == "all" and ctx.author.id != 818919767784161293:
        print(f"[-] {bcolors.BOLD}DEBUG: {ctx.author}{bcolors.ENDC} {ctx.content}".replace('\n', '\n │  '))
        await bot.get_channel(826426599502381056).send(f"[-] DEBUG: {ctx.author.mention}\n```{ctx.content}```")

    # BANNED WORDS
    with open('assets/BadWords.txt', 'r') as f:
        badwords = f.read().split()
        for word in badwords:
            if word in ctx.content:
                await ctx.delete()
                await ctx.channel.send("Don't say that :(")

    await bot.process_commands(ctx)  # Processes the commands


# ERROR HANDLING -----------------------------------------------------------------------------------
@bot.event
async def on_command_error(ctx, error):
    # If the command does not exist/is not found.
    if isinstance(error, CommandNotFound):
        await ctx.message.add_reaction("❓")
    # If the command is on cooldown.
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=discord.Embed(title=f"Slow down!", description=f"Try again in {error.retry_after:.2f}s.", color=0xeb4034))
    elif isinstance(error, MemberNotFound):
        await ctx.reply("That's not a valid member!")
    elif isinstance(error, MessageNotFound):
        await ctx.send("Did you delete your message? ")
    elif isinstance(error, MissingPermissions):
        await ctx.reply("Thonk says you don't have the required permissions to perform this command :pensive:")
    else:  # If its a actual error.
        try:
            embed = discord.Embed(colour=0xff0000, timestamp=ctx.message.created_at,
                                  title="**An error occurred!** Please notify Fripe if necessary.")
            embed.add_field(name="Error:", value=f"```{error}```")
            embed.set_footer(text=f"Caused by {ctx.author}")
            await ctx.send(embed=embed)  # Send error in chat
        except Exception:  # When big oops happens (aka it fails to send the error in caht)
            print(f"{bcolors.WARNING + bcolors.BOLD}Failed to send chat message{bcolors.ENDC}")
        finally:  # Print error to console
            formatederror = "".join(format_exception(type(error), error, error.__traceback__)).rstrip()
            print(f"{bcolors.FAIL}{bcolors.ENDC + bcolors.FAIL}{formatederror}{bcolors.ENDC}")


# COMMAND LOGGING -----------------------------------------------------------------------------------
@bot.event
async def on_command_completion(ctx):
    print(f"Command was executed by {bcolors.OKCYAN}{ctx.message.author}\n{bcolors.HEADER}{ctx.message.content}{bcolors.ENDC}")
    if debug == "cmd":
        embed = discord.Embed(colour=0xff0000, timestamp=ctx.message.created_at,
                              title=f"Command was executed by {ctx.author}")
        embed.add_field(name=f"https://discordapp.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}",
                        value=f"**Command:**\n```{ctx.message.content}```")
        embed.set_footer(text=f"Ran by {ctx.author.mention}")
        await bot.get_channel(830391075267936266).send(embed=embed)


# COMMANDS -----------------------------------------------------------------------------------

# Nothing here :crabrave:

# RUN THE BOT -----------------------------------------------------------------------------------
load_dotenv()
bot.run(os.getenv('TOKEN'))