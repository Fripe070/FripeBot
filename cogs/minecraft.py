import base64
import contextlib
import io
import json
import re
import time
from gzip import BadGzipFile

import discord
import python_nbt.nbt
import requests
from discord.ext import commands

from assets.stuff import config


class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def mcstatus(self, ctx: commands.Context):
        msg = await ctx.reply("Geting statuses from the websites... <a:loading:894950036964782141>")

        mc_sites = {
            "Auth server": "authserver.mojang.com",
            "Session server": "sessionserver.mojang.com/session/minecraft/profile/8667ba71b85a4004af54457a9734eed7",
            "Xbox Live": "xnotify.xboxlive.com/servicestatusv6/US/en-US",
            "Mojang API": "api.mojang.com/users/profiles/minecraft/steve",
            "Libraries": "libraries.minecraft.net",
            "Piston Meta": "piston-meta.mojang.com/mc/game/version_manifest.json",
            "Launcher Meta": "launchermeta.mojang.com/mc/game/version_manifest.json",
        }

        embed = discord.Embed(
            title="Responses from the different minecraft related websites.",
            description="",
            colour=ctx.author.colour,
            timestamp=ctx.message.created_at,
        )
        embed.set_footer(text=f"Command executed by: {ctx.author.display_name}")

        for name, url in mc_sites.items():
            try:
                await msg.edit(content=f"Getting {name.lower()} status <a:loading:894950036964782141>")
                r = requests.get(f"https://{url}", timeout=2)

                if r.ok:
                    embed.description += f"**{name}:** ✅\n"
                else:
                    embed.description += (
                        f"**{name}:**\n<:YellowCheckmark:999549006495629372> {r.status_code} {r.reason}.\n"
                    )

            except requests.exceptions.Timeout:
                embed.description += f"**{url}:**\n<:RedX:999549005342187620> Timed out.\n"
            except requests.exceptions.RequestException as error:
                embed.description += (
                    f"**{url}:**\n<:RedX:999549005342187620> There was an error. Error: {error.response}\n"
                )

            await msg.edit(embed=embed)
        await msg.edit(content=None)

    @commands.command(aliases=["mcplayer", "mcuser", "mcusr"])
    async def playerinfo(self, ctx: commands.Context, player):
        await ctx.message.add_reaction("<a:loading:894950036964782141>")
        msg = await ctx.send("Fetching player UUID... (this might take a while)")
        url = f"https://api.mojang.com/users/profiles/minecraft/{player}"

        try:
            uuid = requests.get(url).json()["id"]
        except Exception:
            if requests.get(f"https://api.mojang.com/user/profiles/{player}/names"):
                uuid = player
            else:
                await ctx.reply("That username is not taken.")
                await msg.delete()
                return

        await msg.edit(content="Fetching player names... (this might take a while)")
        url = f"https://api.mojang.com/user/profiles/{uuid}/names"
        tmprequest = requests.get(url).json()
        pastnames = []
        for name in tmprequest:
            if "changedToAt" in name:
                pastnames.append(f"{name['name']} (<t:{int(name['changedToAt']) // 1000}:R>)")
            else:
                pastnames.append(name["name"])

        oldestname = pastnames[0]
        pastnames.reverse()
        pastnamesstring = ""

        i = 0
        for name in pastnames:
            i += 1
            if name != oldestname:
                if (
                    len(
                        f"{pastnamesstring}{name}\n{oldestname} and {len(pastnames[i:])} more\n\n**Original:**\n{oldestname}"
                    )
                    < 1020
                ):
                    pastnamesstring += f"{name}\n"
                else:
                    pastnamesstring += f"and {len(pastnames[i:])} more\n"
                    break

        pastnamesstring += f"\n**Original name:**\n{oldestname}"

        await msg.edit(content="Fetching player model info... (this might take a while)")

        url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
        tmprequest = requests.get(url).json()
        skincape = tmprequest["properties"][0]["value"]
        skincape = json.loads(base64.b64decode(skincape).decode("utf-8"))
        username = tmprequest["name"]

        await msg.edit(content="Fetching player model type... (this might take a while)")
        try:
            if skincape["textures"]["SKIN"]["metadata"] == {"model": "slim"}:
                playermodel = "Slim"
            else:
                playermodel = "Classic"
        except KeyError:
            playermodel = "Classic"

        embed_desc = f"**Player name:** {username}\n**UUID:** `{uuid}`\n\n**Player model:** {playermodel}\n"

        await msg.edit(content="Fetching player skin... (this might take a while)")
        if "SKIN" in skincape["textures"]:
            embed_desc += f'**Skin:** [link]({skincape["textures"]["SKIN"]["url"]})\n'

        await msg.edit(content="Fetching player cape... (this might take a while)")
        if "CAPE" in skincape["textures"]:
            cape_url = skincape["textures"]["CAPE"]["url"]
            migrator = "2340c0e03dd24a11b15a8b33c2a7e9e32abb2051b2481d0ba7defd635ca7a933"
            minecon11 = "953cac8b779fe41383e675ee2b86071a71658f2180f56fbce8aa315ea70e2ed6"
            minecon12 = "a2e8d97ec79100e90a75d369d1b3ba81273c4f82bc1b737e934eed4a854be1b6"
            minecon13 = "153b1a0dfcbae953cdeb6f2c2bf6bf79943239b1372780da44bcbb29273131da"
            minecon15 = "b0cc08840700447322d953a02b965f1d65a13a603bf64b17c803c21446fe1635"
            minecon16 = "e7dfea16dc83c97df01a12fabbd1216359c0cd0ea42f9999b6e97c584963e980"
            realmsmapmaker = "17912790ff164b93196f08ba71d0e62129304776d0f347334f8a6eae509f8a56"
            mojang = "5786fe99be377dfb6858859f926c4dbc995751e91cee373468c5fbf4865e7151"
            translator = "1bf91499701404e21bd46b0191d63239a4ef76ebde88d27e4d430ac211df681e"
            mojangclassic = "8f120319222a9f4a104e2f5cb97b2cda93199a2ee9e1585cb8d09d6f687cb761"
            mojangstudios = "9e507afc56359978a3eb3e32367042b853cddd0995d17d0da995662913fb00f7"
            mojira = "ae677f7d98ac70a533713518416df4452fe5700365c09cf45d0d156ea9396551"

            if cape_url.endswith(migrator):
                embed_desc += "**Cape:** [migrator]"
            elif cape_url.endswith(minecon11):
                embed_desc += "**Cape:** [MineCon 2011]"
            elif cape_url.endswith(minecon12):
                embed_desc += "**Cape:** [MineCon 2012]"
            elif cape_url.endswith(minecon13):
                embed_desc += "**Cape:** [MineCon 2013]"
            elif cape_url.endswith(minecon15):
                embed_desc += "**Cape:** [MineCon 2015]"
            elif cape_url.endswith(minecon16):
                embed_desc += "**Cape:** [MineCon 2016]"
            elif cape_url.endswith(realmsmapmaker):
                embed_desc += "**Cape:** [Realms Mapmaker]"
            elif cape_url.endswith(mojang):
                embed_desc += "**Cape:** [Mojang]"
            elif cape_url.endswith(mojangclassic):
                embed_desc += "**Cape:** [Mojang (Classic)]"
            elif cape_url.endswith(mojangstudios):
                embed_desc += "**Cape:** [Mojang Studios]"
            elif cape_url.endswith(translator):
                embed_desc += "**Cape:** [Translator]"
            elif cape_url.endswith(mojira):
                embed_desc += "**Cape:** [Mojira Moderator]"
            else:
                embed_desc += "**Cape:** [Other]"

            embed_desc += f'({skincape["textures"]["CAPE"]["url"]})\n'

        await msg.edit(content="Applying embed description... (this might take a while)")
        embed = discord.Embed(
            title=f'Minecraft user information for player "{username}"',
            description=embed_desc,
        )

        await msg.edit(content="Applying embed thumbnail... (this might take a while)")
        with contextlib.suppress(KeyError):
            embed.set_thumbnail(url=f"https://crafatar.com/renders/body/{uuid}?overlay")
        embed.add_field(name="Name history:", value=pastnamesstring)

        await msg.edit(content="Fetching player info from the hypixel API... (this might take a while)")
        with contextlib.suppress(KeyError):
            # HYPIXEL
            url = f"https://api.slothpixel.me/api/players/{uuid}"
            hypixel = requests.get(url).json()

            if hypixel["online"]:
                last_seen = "Now"
            else:
                last_seen = f"<t:{round(hypixel['last_logout'] / 1000)}:R>" if hypixel["last_logout"] else None

            status = f"""{'Online' if hypixel['online'] else 'Offline'} \
    {f'since {last_seen}' if last_seen is not None and not hypixel['online'] else ''}"""

            url = f"https://api.slothpixel.me/api/players/{uuid}/status"
            playing = requests.get(url).json()["game"]["type"] if hypixel["online"] else None
            embed.add_field(
                name="Hypixel:",
                value=f"""**Status:** {status}
**Currectly playing:** {playing if hypixel['online'] and playing is not None else 'Nothing'}
**Rank:** {hypixel['rank'].replace('_PLUS', '+') if hypixel['rank'] else ''}
**Level:** {int(hypixel['level'])}
**Exp:** {hypixel['exp']}
**Total coins:** {hypixel['total_coins']}
**Karma:** {hypixel['karma']}
**Mc version:** {hypixel['mc_version'] or 'Unknown'}""",
            )

        await msg.delete()
        embed.set_footer(text=f"Command executed by: {ctx.author.display_name}")
        await ctx.reply(embed=embed)

    @commands.command()
    async def mcserver(self, ctx: commands.Context, ip=None, port=None):
        if ip is None:
            await ctx.reply("You have to specify a server ip.")
            return

        url = f"https://api.mcsrvstat.us/2/{ip}"

        if port is not None:
            url += f":{port}"

        r = requests.get(url)
        server = r.json()

        if server["online"] is False:
            if port:
                await ctx.reply("Server is currently offline, did you use the correct port?")
            else:
                await ctx.reply("Server is currently offline.")
            return

        motd = "".join(i.strip() + "\n" for i in server["motd"]["clean"])
        try:
            location = requests.get(f"https://geolocation-db.com/jsonp/{server['ip']}").content.decode("utf-8")
            location = json.loads(location.split("(")[1].strip(")"))
        except Exception:
            location = None

        embed_desc = f"""
**Server ip:** \"{server["hostname"]}\" ({server["ip"]})
**Port:** `{server["port"]}`
"""
        if location:
            embed_desc += f"\n**Location:** {location['country_name']}"

        embed_desc += f"""
**Version:** {server['version']}
**Players:** {server['players']['online']}/{server['players']['max']}
"""
        if "list" in server["players"]:
            embed_desc += f"**Player list:** ```\n{', '.join(server['players']['list'])}\n```\n"

        if "software" in server:
            if server["software"] == "Vanilla" and "mods" in server:
                embed_desc += f"**Software:** {server['software']} (probably not true)\n"
            else:
                embed_desc += f"**Software:** {server['software']}\n"

        if "map" in server:
            embed_desc += f"**Current map:** {server['map']}\n"

        if "mods" in server:
            embed_desc += f"**Mods:** {len(server['mods']['names'])}\n"

        embed_desc += f"""
**Motd:** ```
{motd}
```
"""

        embed = discord.Embed(title=f'Info about server "{ip}"', description=embed_desc)

        await ctx.reply(embed=embed)

    @commands.command()
    async def mcinfo(self, ctx: commands.Context):
        url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
        r = requests.get(url)

        mcversion = r.json()

        embed = discord.Embed(
            title="Minecraft info",
            description=f"""
Latest release: {mcversion["latest"]['release']}
Latest snapshot: {mcversion["latest"]['snapshot']}
Full release date: <t:1321614000:D> (<t:1321614000:R>)
First went public: <t:1242554400:D> (<t:1242554400:R>)
""",
        )

        await ctx.reply(embed=embed)

    @commands.command(aliases=["nbt", "nbttojson", "jsonnbt", "nbtjson"])
    async def nbtread(self, ctx: commands.Context):
        file = await ctx.message.attachments[0].to_file()
        try:
            nbt = python_nbt.nbt.read_from_nbt_file(file.fp)
        except BadGzipFile:
            await ctx.reply("This file is not a valid NBT file.")
            return
        nbt = json.loads(str(nbt).replace('"', '\\"').replace("'", '"'))
        nbt = json.dumps(nbt, indent=4)
        if len(str(nbt)) > 3988:
            await ctx.reply(file=discord.File(io.BytesIO(nbt.encode("utf-8")), filename="nbt.json"))
        else:
            await ctx.reply(f"```json\n{nbt}\n```")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if not config["mojira"]:
            return
        projects = [
            "BDS",  # Bedrock Dedicated Server
            "MCPE",  # Minecraft (Bedrock codebase)
            "MCCE",  # Minecraft Console Edition
            "MCD",  # Minecraft Dungeons
            "MCL",  # Minecraft Launcher
            "REALMS",  # Minecraft Realms
            "MC",  # Minecraft: Java Edition
            "WEB",  # Mojang Web Services
        ]
        issues = []
        for project in projects:
            issues += re.findall(rf"(?:{'|'.join(self.bot.command_prefix)})({project}-\d+)", message.content)
        for issue in issues:
            r = requests.get(f"https://bugs.mojang.com/rest/api/latest/issue/{issue}").json()
            if "errorMessages" in r:
                return
            r = r["fields"]

            desc = re.sub(r"/\s*[\r\n]/gm", "\n", r["description"])
            desc = re.sub(r"h[1-6]\..*\n", "", desc)
            desc = re.sub("", "", desc)
            # Removes mod comments
            desc = re.sub(
                r"""{panel:title=[a-zA-Z]
                    |borderStyle=[a-zA-Z]
                    |borderColor=#[a-zA-Z0-9]
                    |titleBGColor=#[a-zA-Z0-9]
                    |bgColor=#[a-zA-Z0-9]}""",
                "",
                desc,
                flags=re.VERBOSE,
            )
            desc = desc.replace("{noformat}", "```")
            desc = "\n".join(desc.split("\n")[:2])

            embed = discord.Embed(
                title=f"[{issue}] {discord.utils.escape_markdown(r['summary'])}",
                url=f"https://bugs.mojang.com/browse/{issue}",
                description=desc,
                colour=0x30CB72,
            )

            if r["resolution"] is not None:
                embed.add_field(
                    name="Status:",
                    value=f"Resolved as **{r['resolution']['name']}** <t:{round(time.mktime(time.strptime(r['resolutiondate'], '%Y-%m-%dT%H:%M:%S.%f%z')))}:R>",
                )
                if r["fixVersions"]:
                    embed.add_field(name="Fix version:", value=r["fixVersions"][0]["name"])
            else:
                embed.add_field(name="Status:", value="Open")
            embed.add_field(
                name="Created:",
                value=f"<t:{round(time.mktime(time.strptime(r['created'], '%Y-%m-%dT%H:%M:%S.%f%z')))}:R>",
            )

            await message.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Minecraft(bot))
