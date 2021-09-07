from assets.stuff import *

# COG LOADING  -----------------------------------------------------------------------------------
reloads = []
for cog in getcogs():
    try:
        bot.load_extension(cog.replace('\\', '.').replace('/', '.'))
        reloads.append(f"{bcolors.OKBLUE}│ {bcolors.OKGREEN}{cog}")
    except Exception as error:
        reloads.append(f"{bcolors.FAIL}│ {bcolors.WARNING}{error}")


# ON Ready -----------------------------------------------------------------------------------
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
async def on_message(message):
    if message.author != bot.user:
        # Detect if the bot is pinged in the message
        if f"<@{bot.user.id}>" in message.content or f"<@!{bot.user.id}>" in message.content:
            await message.add_reaction("<:ping_gun:823948139504861225>")
            await message.reply("My prefix is `f!`")

        if isinstance(message.channel, discord.channel.DMChannel):  # If message was send in a dm
            print(f"{message.author} Send this in a DM: {message.content}")

        if message.content == "🤡":
            await message.reply("https://cdn.discordapp.com/attachments/776166607448965133/862286194422710272/argument.mp4")
    await bot.process_commands(message)  # Processes the commands


# ERROR HANDLING -----------------------------------------------------------------------------------
@bot.event
async def on_command_error(ctx, error):  # TODO Maybe use a dict for error handling or something idk
    # If the command does not exist/is not found.
    if isinstance(error, CommandNotFound):
        await ctx.message.add_reaction("❓")
    # If the command is on cooldown.
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=discord.Embed(title=f"Slow down!",
                                           description=f"Try again in {error.retry_after:.2f}s.",
                                           color=0xeb4034))
    elif isinstance(error, MemberNotFound):
        await ctx.reply("That's not a valid member!")
    elif isinstance(error, MessageNotFound):
        await ctx.send("Did you delete your message? ")
    elif isinstance(error, MissingPermissions):
        await ctx.reply("You don't have the required permissions to perform this command! :pensive:")
    elif TimeoutError:
        pass
    elif isinstance(error, NotOwner):
        await ctx.message.add_reaction("🔐")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '🔑'

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        except TimeoutError:
            print("E")
            pass
        else:
            await bot.invoke(ctx)
    else:  # If its a actual error
        await senderror(ctx, error)


# COMMAND LOGGING -----------------------------------------------------------------------------------
@bot.event
async def on_command_completion(ctx):
    print(f"Command was executed by {bcolors.OKCYAN}{ctx.message.author}\n{bcolors.HEADER}{ctx.message.content}{bcolors.ENDC}")


# COMMANDS -----------------------------------------------------------------------------------
class Help(commands.HelpCommand):  # TODO Put this in a cog
    def get_command_signature(self, command):
        return command.qualified_name

    async def send_command_help(self, command):
        embed = discord.Embed(title=f"Info about: {self.get_command_signature(command)}")
        if command.help is not None:
            embed.description(value=command.help)
        else:
            embed.description(value="This command doesnt have any further info.")
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", colour=discord.Color.blue())
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value=", ".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)


bot.help_command = Help()

"""
@bot.command()
async def reactiontest(ctx):
    await ctx.send('Send me that 👍 reaction, mate')

    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) == '👍'

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except TimeoutError:
        print("E")
        pass
    else:
        await bot.invoke(help)
"""

# RUN THE BOT -----------------------------------------------------------------------------------
load_dotenv()
bot.run(os.getenv('TOKEN'))
