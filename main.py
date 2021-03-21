import discord
import os
import json
import sys
from discord.ext import commands
from discord.ext.commands import *

with open("config.json") as f:
    config = json.load(f)

prefix = config["prefixes"]
trusted = config["trusted"]

bot = commands.Bot(
    command_prefix=prefix,
    case_insensitive=True,
)

with open('token.txt', 'r') as f:
    TOKEN = f.read()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'

@bot.event
async def on_ready():
    print(f'''{bcolors.BOLD + bcolors.OKBLUE}Connected successfully!
Logged in as {bcolors.OKCYAN}{bot.user.name}{bcolors.OKBLUE}, with the ID {bcolors.OKCYAN}{bot.user.id}{bcolors.ENDC}''')
    status = f'you 👀'
    await bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.watching))
    print(f'{bcolors.BOLD + bcolors.OKBLUE}Status set to "{bcolors.OKCYAN}watching {status}{bcolors.OKBLUE}"{bcolors.ENDC}')
    print(f"{bcolors.BOLD + bcolors.OKBLUE}------------------------------------------------------{bcolors.ENDC}")


#ERROR HANDLING -------------------------------------------------------------------------------------------------------------


@bot.event
async def on_command_error(ctx, error):
    # If the command does not exist/is not found.
    if isinstance(error, CommandNotFound):
        await ctx.message.add_reaction("❓")
    else:
        try:
            await ctx.send(f"""An error occurred!** :flushed: Please notify Fripe if necessary.
Error:```{error}```""")
        except Exception as criticalexception:
            print(f"""Couldn't send error message. error:
{criticalexception}""")
        finally:
            print(f"Error: {error}")






#COMMANDS -------------------------------------------------------------------------------------------------------------------


@bot.command(help="Command to see if the bot is responding")
async def test(ctx):
    await ctx.message.add_reaction('👍')


@bot.command(help="Displays the bots ping")
async def ping(ctx):
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


@bot.command(aliases=['Hi'], help="Says hi")
async def hello(ctx):
    await ctx.message.add_reaction('👋')
    await ctx.reply(f"Hello {ctx.author.name} 👋")


@bot.command(help="Gives soup")
async def soup(ctx):
    await ctx.reply("Here's your soup! <:soup:823158453022228520>")


@bot.command(help="Displays information about a discord user")
async def whois(ctx, member: discord.Member = None):
    if not member:  # if member is no mentioned
        member = ctx.message.author  # set member as the author
    embed = discord.Embed(colour=0x00ffff, timestamp=ctx.message.created_at,
                          title=f"User Info - {member}")
    embed.set_thumbnail(url=f"{member.avatar_url}")
    embed.set_footer(text=f"Requested by {ctx.author}")
    embed.add_field(name="Username:", value=member.name)
    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Account Created At:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    await ctx.send(embed=embed)


@bot.command(aliases=['Say'], help="Makes the bot say things")
async def echo(ctx, *, tell):
    if ctx.author.id in trusted:
        if isinstance(ctx.channel, discord.channel.DMChannel):
            print(f'{bcolors.BOLD + bcolors.WARNING + ctx.author + bcolors.ENDC + bcolors.FAIL} Tried to make me say: "{bcolors.WARNING + bcolors.BOLD + tell + bcolors.ENDC + bcolors.FAIL}" In a dm{bcolors.ENDC}"')
            await ctx.send("That command isn't available in dms")
        else:
            print(f'{bcolors.BOLD + bcolors.OKCYAN}{ctx.author}{bcolors.ENDC} Made me say: "{bcolors.OKBLUE + bcolors.BOLD}{tell}{bcolors.ENDC}"')
            await ctx.message.delete()
            await ctx.send(tell)
    else:
        print(f'{bcolors.BOLD}{bcolors.WARNING}{ctx.author}{bcolors.ENDC}{bcolors.FAIL} Tried to make me say: "{bcolors.WARNING}{bcolors.BOLD}{tell}{bcolors.ENDC}{bcolors.FAIL}" But '"wasnt"f' allowed to{bcolors.ENDC}"')
        await ctx.message.add_reaction("🔐")


@bot.command(aliases=['Exec'], help="Executes code")
async def execute(ctx, *, arg):
    if ctx.author.id in trusted:
        print(f'{bcolors.OKGREEN}Trying to run code "{bcolors.OKCYAN}{arg}{bcolors.OKGREEN}"{bcolors.ENDC}')
        try:
            exec(arg)
            await ctx.message.add_reaction("<:yes:823202605123502100>")
        except Exception as error:
            print(f"Error occurred during execution: {error}")
            await ctx.send(f"An error occurred during execution```\n{error}\n```")
            await ctx.message.add_reaction("<:no:823202604665929779>")
    else:
        print(f'{bcolors.FAIL}{ctx.author.name}{bcolors.WARNING} Tried to run code "{bcolors.FAIL}{arg}{bcolors.WARNING}"{bcolors.ENDC}')
        await ctx.message.add_reaction("🔐")


@bot.command(aliases=['Eval'], help="Executes code")
async def evaluate(ctx, *, arg):
    if ctx.author.id in trusted:
        print(f'{bcolors.OKGREEN}Trying to evaluate "{bcolors.OKCYAN}{arg}{bcolors.OKGREEN}"{bcolors.ENDC}')
        try:
            await ctx.send(eval(arg))
            await ctx.message.add_reaction("<:yes:823202605123502100>")
        except Exception as error:
            print(f"Error occurred during evaluation: {error}")
            await ctx.send(f"An error occurred during evaluation```\n{error}\n```")
            await ctx.message.add_reaction("<:no:823202604665929779>")
    else:
        print(f'{bcolors.FAIL}{ctx.author.name}{bcolors.WARNING} Tried to evaluate "{bcolors.FAIL}{arg}{bcolors.WARNING}"{bcolors.ENDC}')
        await ctx.message.add_reaction("🔐")


@bot.command(help="Restarts the bot") # Currently not working
async def restart(ctx):
    if ctx.author.id in trusted:
        await ctx.message.add_reaction("👍")
        await ctx.reply("Restarting! :D")
#        os.execv(sys.executable, ['python'] + sys.argv)
#        os.execv("main.py", sys.argv)
        exit(0)
    else:
        await ctx.message.add_reaction("🔐")


@bot.command(aliases=['die', 'kill'], help="Stops the bot")
async def stop(ctx):
    if ctx.author.id in trusted:
        await ctx.message.add_reaction("👍")
        await ctx.reply("Ok. :(")
        print(f"{bcolors.FAIL + bcolors.BOLD}{ctx.author.name} Told me to stop{bcolors.ENDC}")
        await bot.close()
    else:
        await ctx.message.add_reaction("🔐")


bot.run(TOKEN)