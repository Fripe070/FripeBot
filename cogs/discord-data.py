import discord
import requests
import json
import re
import time

from discord.ext import commands
from discord.ext import tasks
from main import config


class DiscordData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.experiments.start()
        self.hash = ""

    def cog_unload(self):
        self.experiments.cancel()

    async def extractexperiments(self, js: str) -> list:
        rawexperiments = re.findall(
            r"\.(default|createExperiment|register(?:User|Guild)Experiment)\)\(({.+?})\)(?:;|}|,[a-zA-Z_]{1,4}=)", js
        )
        # print(json.dumps(rawexperiments, indent=4))
        if not rawexperiments:
            return []
        try:
            with open("assets/experiments.json", "r") as f:
                experiments = json.load(f)
        except TypeError:
            experiments = []
        print(experiments)
        for rawexperiment in rawexperiments:
            if rawexperiment[0] == "default" and "kind:" not in rawexperiment[1]:
                continue
            # print(rawexperiment[1])
            exp = re.sub(
                r"!0",
                "true",
                re.sub(
                    r"!1",
                    "false",
                    re.sub(
                        r",clientFilter:.*",
                        "}",
                        re.sub(
                            r"[a-zA-Z_]+\.ExperimentBuckets\.([A-Z\d_]+)",
                            0 if r"\1" == "CONTROL" else r"\1"[-1:],
                            re.sub(
                                r"(\w+)(?=:[\"\[{!\d(?:true)(?:false)].*[\"\]},])",
                                r'"\1"',
                                rawexperiment[1],
                                flags=re.ASCII,
                            ),
                        ),
                    ),
                ),
            )
            print(exp)
            exp = json.loads(exp)
            if exp["id"] not in experiments:
                experiments.append(exp)

        print(json.dumps(experiments, indent=4))
        with open("assets/experiments.json", "w") as f:
            json.dump(experiments, f, indent=4)
        return experiments

    @tasks.loop(minutes=5)
    # @tasks.loop(seconds=5)
    async def experiments(self):
        new_hash = requests.get(f"https://canary.discord.com/assets/version.canary.json?_={int(time.time())}").json()[
            "hash"
        ]

        if self.hash == new_hash:
            return
        else:
            self.hash = new_hash

        r = requests.get(f"https://canary.discord.com/app?_={int(time.time())}")
        html = r.text
        # js = requests.get(f"https://canary.discord.com{script}").text
        js = open("build_id.txt", "r", encoding="utf-8").read()
        build_id = re.search(r"Build Number: (?P<ID>\d+)", js).group(0)
        experiments = await self.extractexperiments(js)
        print(json.dumps(experiments, indent=4))
        if not experiments:
            return
        experiment_channel = self.bot.get_channel(int(config["experiments_channel_id"]))
        for experiment in experiments:
            embed = discord.Embed(
                title=f"New {experiment['kind']} experiment: {experiment['label']}",
                description=f"ID: {experiment['id']}\nDefault config: ```json\n{experiment['defaultConfig']}```",
            )
            embed.add_field(
                name="Treatments:",
                value="\n".join(
                    f"Treatment {treatment['id']}: {treatment['label']}" for treatment in experiment["treatments"]
                ),
            )

            embed.set_footer(text=f"{build_id} | {r.headers['Last-Modified']}")

            await experiment_channel.send(embed=embed)

    @experiments.before_loop
    async def before_experiments(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(DiscordData(bot))
