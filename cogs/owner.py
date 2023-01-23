from pathlib import Path

import discord
from discord.ext import commands

from utils import BetterEmbed, get_extension, get_extensions


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def setstatus(self, ctx: commands.Context, activity, *, new_status=None):
        """Sets the bots status"""
        status = new_status

        if activity == "watching":
            self.bot.logger.info(f'Status set to "{activity} {status}')
            await self.bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.watching))
            await ctx.reply(f'Status set to "{activity} {status}"')

        elif activity == "playing":
            self.bot.logger.info(f'Status set to "{activity} {status}')
            await self.bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.playing))
            await ctx.reply(f'Status set to "{activity} {status}"')

        elif activity == "listening":
            self.bot.logger.info(f'Status set to "{activity} to {status}')
            await self.bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.listening))
            await ctx.reply(f'Status set to "{activity} to {status}"')

        elif activity == "competing":
            self.bot.logger.info(f'Status set to "{activity} in {status}')
            await self.bot.change_presence(activity=discord.Activity(name=status, type=discord.ActivityType.competing))
            await ctx.reply(f'Status set to "{activity} in {status}"')
        else:
            await ctx.reply("That's not a valid activity!")

    @staticmethod
    async def extension_fetching_helper(cog_path: Path | str) -> list[str]:
        default_cog_directory = Path("./cogs/")
        cog_path = default_cog_directory / cog_path

        if (
            not cog_path.is_file()
            and not cog_path.is_dir()
            and cog_path.suffix == ""
            and (python_file_path := cog_path.with_suffix(".py")).is_file()
        ):
            cog_path = python_file_path

        if cog_path.is_file():
            return [get_extension(cog_path)]
        elif cog_path.is_dir():
            return get_extensions(cog_path)
        else:
            raise FileNotFoundError

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, *, to_reload: str = "./"):
        """Reloads the bot cog(s) specified"""
        reply_message = await ctx.reply(embed=BetterEmbed(colour=ctx.author, title="Reloading Cog(s)..."))

        try:
            extensions = await self.extension_fetching_helper(to_reload)
        except FileNotFoundError:
            return await ctx.reply("There is no file or directory at the specified location.")

        reloaded_extensions = {}
        for extension in extensions:
            styled_extension_name = "/".join(extension.split(".")[1:])
            try:
                await self.bot.reload_extension(extension)
                self.bot.logger.info(f"Reloaded extension {extension}")
                reloaded_extensions[styled_extension_name] = {"success": True, "error": None}
            except Exception as error:
                self.bot.logger.error(f"Failed to reload extension {extension}: {error}")
                reloaded_extensions[styled_extension_name] = {"success": False, "error": str(error)}

        embed = BetterEmbed(
            title=f"Cog{'s' if len(extensions) > 1 else ''} Reloaded!",
            description="\n".join(
                sorted(
                    f"{'✅' if status['success'] else '❌'} {name} {'' if status['success'] else status['error']}"
                    for name, status in reloaded_extensions.items()
                )
            ),
            colour=ctx.author,
        )

        await reply_message.edit(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: commands.Context, *, to_load: str = "./"):
        """Loads the bot cog(s) specified"""
        reply_message = await ctx.reply(embed=BetterEmbed(colour=ctx.author, title="Loading Cog(s)..."))

        try:
            extensions = await self.extension_fetching_helper(to_load)
        except FileNotFoundError:
            return await ctx.reply("There is no file or directory at the specified location.")

        loaded_extensions = {}
        for extension in extensions:
            styled_extension_name = " ".join(extension.split(".")[1:]).title()
            try:
                await self.bot.load_extension(extension)
                self.bot.logger.info(f"Loaded extension {extension}")
                loaded_extensions[styled_extension_name] = {"success": True, "error": None}
            except Exception as error:
                self.bot.logger.error(f"Failed to load extension {extension}: {error}")
                loaded_extensions[styled_extension_name] = {"success": False, "error": str(error)}

        embed = BetterEmbed(
            title=f"Cog{'s' if len(extensions) > 1 else ''} Loaded!",
            description="\n".join(
                f"{'✅' if status['success'] else '❌'} {name} {'' if status['success'] else status['error']}"
                for name, status in loaded_extensions.items()
            ),
            colour=ctx.author,
        )

        await reply_message.edit(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, *, to_unload: str = "./"):
        """Unloads the bot cog(s) specified"""
        reply_message = await ctx.reply(embed=BetterEmbed(colour=ctx.author, title="Unloading Cog(s)..."))

        try:
            extensions = await self.extension_fetching_helper(to_unload)
        except FileNotFoundError:
            return await ctx.reply("There is no file or directory at the specified location.")

        unloaded_extensions = {}
        for extension in extensions:
            styled_extension_name = " ".join(extension.split(".")[1:]).title()
            try:
                await self.bot.unload_extension(extension)
                self.bot.logger.info(f"Unloaded extension {extension}")
                unloaded_extensions[styled_extension_name] = {"success": True, "error": None}
            except Exception as error:
                self.bot.logger.error(f"Failed to unload extension {extension}: {error}")
                unloaded_extensions[styled_extension_name] = {"success": False, "error": str(error)}

        embed = BetterEmbed(
            title=f"Cog{'s' if len(extensions) > 1 else ''} Unloaded!",
            description="\n".join(
                f"{'✅' if status['success'] else '❌'} {name} {'' if status['success'] else status['error']}"
                for name, status in unloaded_extensions.items()
            ),
            colour=ctx.author,
        )

        await reply_message.edit(embed=embed)

    @commands.command(aliases=["shutdown"])
    @commands.is_owner()
    async def stop(self, ctx: commands.Context):
        """Stops the bot"""
        await ctx.message.add_reaction("👍")
        await ctx.reply("Ok. :(\nShutting down...")
        self.bot.logger.info("Stopping bot.")
        await self.bot.close()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Owner(bot))
