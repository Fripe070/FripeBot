import discord
from discord.ext import commands
from discord.ext.commands import *

from assets.stuff import config


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command(self, ctx):
        print(f"Command was executed by {ctx.message.author}\n{ctx.message.content}")
        embed = discord.Embed(
            title=f"{ctx.author.name} Ran a command in {ctx.channel.name} ({ctx.channel.id})",
            description=ctx.message.content,
            color=ctx.author.color
        )
        embed.set_footer(text=f"Message ID: {ctx.message.id}")

        await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

    @Cog.listener()
    async def on_message_delete(self, message):
        if message.author != self.bot.user and message.channel.type != discord.ChannelType.private:
            embed = discord.Embed(
                title=f"Message by {message.author.name} was deleted in {message.channel.name} ({message.channel.id})",
                description=message.content,
                color=message.author.color
            )
            if message.reference is not None:
                ref = await message.channel.fetch_message(message.reference.message_id)
                embed.add_field(
                    name=f"Replying to {ref.author.name} ({ref.author.id}), message content:",
                    value=ref.content
                )
                embed.set_footer(text=f"Message ID: {message.id}, replied to message ID: {ref.id}")
            else:
                embed.set_footer(text=f"Message ID: {message.id}")

            await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

    @Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author != self.bot.user and before.channel.type != discord.ChannelType.private:
            embed = discord.Embed(
                title=f"Message by {before.author.name} was edited in {before.channel.name} ({before.channel.id})",
                color=before.author.color
            )
            embed.add_field(name="Before", value=f"{before.content}")
            embed.add_field(name="After", value=f"{after.content}")
            embed.set_footer(text=f"Message ID: {before.id}")

            await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            embed = discord.Embed(
                title=f"{before.name} changed their nickname",
                description=f"Before: {before.nick}\nAfter: {after.nick}",
                color=before.color
            )
            embed.set_footer(text=f"User ID: {before.id}")

            await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)
        if before.roles != after.roles:
            embed_desc = f"Before: {', '.join([role.mention for role in before.roles[1:]])}\n"
            embed_desc += f"After: {', '.join([role.mention for role in after.roles[1:]])}\n"
            diff = set(before.roles[1:]).symmetric_difference(set(after.roles[1:]))
            embed_desc += f"Differance: {', '.join([role.mention for role in diff])}"

            embed = discord.Embed(
                title=f"{before.name} changed their roles",
                description=embed_desc,
                color=after.color
            )
            embed.set_footer(text=f"User ID: {before.id}")

            await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

    @Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:
            embed = discord.Embed(
                title=f"{before.name} changed their name",
                description=f"Before: {before.name}\nAfter: {after.name}",
                color=before.color
            )
            embed.set_footer(text=f"User ID: {before.id}")

            await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

        if before.discriminator != after.discriminator:
            embed = discord.Embed(
                title=f"{before.name} changed their discriminator",
                description=f"Before: {before.discriminator}\nAfter: {after.discriminator}",
                color=before.color
            )
            embed.set_footer(text=f"User ID: {before.id}")

            await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

        if before.avatar != after.avatar:
            embed = discord.Embed(
                title=f"{before.name} changed their avatar",
                description=f"Before: {before.avatar_url}\nAfter: {after.avatar_url}",
                color=before.color
            )
            embed.set_footer(text=f"User ID: {before.id}")

            await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

    @Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title=f"{member.name} joined {member.guild.name}",
            color=member.color
        )
        embed.set_footer(text=f"User ID: {member.id}, Guild ID: {member.guild.id}")

        await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

    @Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title=f"{member.name} left {member.guild.name}",
            color=member.color
        )
        embed.set_footer(text=f"User ID: {member.id}, Guild ID: {member.guild.id}")

        await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

    @Cog.listener()
    async def on_guild_update(self, before, after):
        if before.name != after.name:
            embed = discord.Embed(
                title=f"{before.name} changed it's name",
                description=f"Before: {before.name}\nAfter: {after.name}"
            )
            embed.set_footer(text=f"Guild ID: {before.id}")

            await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

        if before.icon != after.icon:
            embed = discord.Embed(
                title=f"{before.name} changed it's icon",
                description=f"Before: {before.icon_url}\nAfter: {after.icon_url}"
            )
            embed.set_footer(text=f"Guild ID: {before.id}")

            await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

    @Cog.listener()
    async def on_guild_role_create(self, role):
        embed = discord.Embed(
            title=f"{role.name} was created in {role.guild.name}",
            description=f"Role ID: {role.id}",
            colour=role.color
        )
        embed.set_footer(text=f"Guild ID: {role.guild.id}")

        await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

    @Cog.listener()
    async def on_guild_role_delete(self, role):
        embed = discord.Embed(
            title=f"{role.name} was deleted in {role.guild.name}",
            description=f"Role ID: {role.id}",
            colour=role.color
        )
        embed.set_footer(text=f"Guild ID: {role.guild.id}")

        await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

    @Cog.listener()
    async def on_guild_role_update(self, before, after):
        if before.name != after.name:
            embed = discord.Embed(
                title=f"Role {before.name} changed name",
                description=f"Before: {before.name}\nAfter: {after.name}",
                colour=after.color
            )
            embed.set_footer(text=f"Guild ID: {before.guild.id}")

            await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

        if before.color != after.color:
            embed = discord.Embed(
                title=f"Role {before.name} changed color",
                description=f"Before: {before.color}\nAfter: {after.color}",
                colour=after.color
            )
            embed.set_footer(text=f"Guild ID: {before.guild.id}")

            await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

        if before.permissions != after.permissions:
            embed = discord.Embed(
                title=f"Role {before.name} changed permissions",
                description=f"Before Value: {before.permissions.value}\nAfter Value: {after.permissions}",
                colour=after.color
            )
            embed.set_footer(text=f"Guild ID: {before.guild.id}")

            await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

    @Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(
            title=f"{user.name} was banned from {guild.name}",
            colour=user.color
        )
        embed.set_footer(text=f"User ID: {user.id}, Guild ID: {guild.id}")

        await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)

    @Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(
            title=f"{user.name} was unbanned from {guild.name}",
            colour=user.color
        )
        embed.set_footer(text=f"User ID: {user.id}, Guild ID: {guild.id}")

        await self.bot.get_channel(int(config["logging_channel_id"])).send(embed=embed)


def setup(bot):
    bot.add_cog(Logging(bot))
