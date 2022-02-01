import discord
import os

from discord.ext import commands
from dotenv import load_dotenv
from assets.stuff import config, col, getcogs

bot = commands.Bot(
    command_prefix=config["prefixes"],
    case_insensitive=True,
    intents=discord.Intents.all(),
    strip_after_prefix=True
)

# COG LOADING  -----------------------------------------------------------------------------------
reloads = []
for cog in getcogs():
    try:
        bot.load_extension(cog.replace('\\', '.').replace('/', '.'))
        reloads.append(f"{col.BLUE}│ {col.GREEN}{cog}")
    except Exception as error:
        reloads.append(f"{col.FAIL}│ {col.WARN}{error}")


# ON Ready -----------------------------------------------------------------------------------
@bot.event
async def on_ready():
    status = f'you. And {len(bot.guilds)} servers 👀'
    await bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.watching))
    print(f'''{col.BOLD + col.BLUE}Connected successfully!
Logged in as {col.CYAN}{bot.user.name}{col.BLUE}, with the ID {col.CYAN}{bot.user.id}
{col.BLUE}Status set to "{col.CYAN}watching {status}{col.BLUE}"
Cogs:
''' + "\n".join(reloads) + f"\n{col.BLUE}└───────────────────────────────────────────────────────{col.ENDC}")


# ERROR HANDLING -----------------------------------------------------------------------------------
@bot.event
async def on_command_error(ctx, error):
    # If the command does not exist/is not found.
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction("❓")
    elif isinstance(error, commands.NotOwner):
        await ctx.message.add_reaction("🔐")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(embed=discord.Embed(
            title=f"Slow down!",
            description=f"Try again in {error.retry_after:.2f}s.",
            color=0xeb4034
        ))
    elif isinstance(error, commands.MemberNotFound) or isinstance(error, commands.UserNotFound):
        await ctx.reply("That's not a valid user!")
    elif isinstance(error, commands.MessageNotFound):
        await ctx.send("Did you delete your message? ")
    elif isinstance(error, TimeoutError):
        pass
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply(error)
    else:
        try:
            embed = discord.Embed(
                title="An error occurred! Please notify Fripe if necessary.",
                description=f"```{error}```",
                timestamp=ctx.message.created_at,
                colour=0xff0000
            )
            embed.set_footer(text=f"Caused by {ctx.author}")
            await ctx.send(embed=embed)
        except Exception:
            print(f"{col.WARN + col.BOLD}Failed to send chat message{col.ENDC}")
        raise error


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

# RUN THE BOT -----------------------------------------------------------------------------------
load_dotenv()
bot.run(os.getenv('TOKEN'))
