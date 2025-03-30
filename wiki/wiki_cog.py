import discord
import string
import re
from datetime import datetime, timedelta
from redbot.core import commands

class FafoView(discord.ui.View):
    def __init__(self, timeout: int = 180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="FAFO", style=discord.ButtonStyle.danger)
    async def click_here(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            until = datetime.utcnow() + timedelta(minutes=5)
            await interaction.user.edit(communication_disabled_until=until)
            await interaction.response.send_message("You have been timed out for 5 minutes.", ephemeral=True)
        except Exception:
            await interaction.response.send_message("Failed to timeout you.", ephemeral=True)

class Wiki(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_roles = [
            "Game Server Team", "Advisors", "Wardens", "The Brute Squad", "Sentinels",
            "Community Manager - Helldivers", "Community Manager - Book Club",
            "Community Manager - Call of Duty", "Community Manager - D&D",
            "Community Manager - World of Warcraft", "Community Manager - Minecraft",
            "Skye", "Librarian Raccoon", "Zara", "BadgerSnacks", "Donnie",
            "Captain Sawbones", "Captain Soulo"
        ]

        self.alias_to_role = {
            "7dtd": "7 Days To Die", "ark": "ARK", "aoe": "Age of Empires", "amongus": "Among Us",
            "acnh": "Animal Crossing", "apex": "Apex Legends", "assetto": "Assetto Corsa",
            "b4b": "Back 4 Blood", "bf": "Battlefield", "bg3": "Baldur's Gate 3", "cod": "Call of Duty",
            "cw": "Content Warning", "dayz": "DayZ", "dbd": "Dead by Daylight", "drg": "Deep Rock Galactic",
            "demo": "Demonologist", "d2": "Destiny 2", "diablo": "Diablo", "dirt": "DiRT",
            "ddv": "Disney Dreamlight Valley", "dnd": "Dungeons&Dragons", "d&d": "Dungeons&Dragons",
            "dungeons": "Dungeons&Dragons", "biweekly": "D&D Biweekly Players", "dragonage": "Dragon Age",
            "dyinglight": "Dying Light", "eldenring": "Elden Ring", "eso": "Elder Scrolls",
            "elite": "Elite Dangerous", "enshrouded": "Enshrouded", "eft": "Escape from Tarkov",
            "tarkov": "Escape from Tarkov", "fallout": "Fallout", "farmingsim": "Farming sim",
            "ffxiv": "Final Fantasy XIV", "descendant": "The First Descendant", "fivem": "FiveM",
            "honor": "For Honor", "fn": "Fortnite", "forza": "Forza", "genshin": "Genshin Impact",
            "recon": "Ghost Recon", "goose": "Goose Goose Duck", "gta": "Grand Theft Auto V",
            "halo": "Halo", "hll": "Hell Let Loose", "helldivers": "Helldivers 2",
            "hogwarts": "Hogwarts Legacy", "jackbox": "Jackbox", "lol": "League of Legends",
            "lethal": "Lethal Company", "lockdown": "Lockdown Protocol", "lostark": "Lost Ark",
            "mtg": "Magic: The Gathering", "mariokart": "Mario Kart", "marvel": "Marvel Rivals",
            "mc": "Minecraft", "monsterhunter": "Monster Hunter", "mk": "Mortal Kombat",
            "nms": "No Man's Sky", "oncehuman": "Once Human", "ow": "Overwatch", "ow2": "Overwatch",
            "palia": "Palia", "palworld": "Palworld", "poe": "Path of Exile", "pavlov": "Pavlov",
            "phasmophobia": "Phasmophobia", "pubg": "Player Unknown Battlegrounds",
            "pokemon": "Pokémon", "raft": "Raft", "rainbow": "Rainbow Six", "r6": "Rainbow Six",
            "ron": "Ready Or Not", "rdo": "Red Dead: Online", "repo": "R.E.P.O", "rl": "Rocket League",
            "runescape": "RuneScape", "rust": "Rust", "satisfactory": "Satisfactory",
            "sot": "Sea of Thieves", "sims": "The Sims", "sm2": "Space Marines 2", "sc": "Star Citizen",
            "stardew": "Stardew Valley", "starfield": "Starfield", "ssb": "Super Smash Bros.",
            "division": "The Division", "tinytina": "Tiny Tina's Wonderlands", "trucksim": "Truck Simulator",
            "valheim": "Valheim", "val": "Valorant", "warframe": "Warframe", "warthunder": "War Thunder",
            "wot": "World of Tanks", "wow": "World of Warcraft"
        }

    def is_authorized(self, ctx):
        return any(role.name in self.allowed_roles for role in ctx.author.roles)

    async def delete_and_check(self, ctx):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if not self.is_authorized(ctx):
            return False
        return True

    async def send_reply(self, ctx, *args, **kwargs):
        """Helper to reply to the original message if the command was run as a reply."""
        if ctx.message.reference:
            try:
                original_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                await original_message.reply(*args, **kwargs)
                return
            except Exception:
                pass
        await ctx.send(*args, **kwargs)

    @commands.command()
    async def lfg(self, ctx):
        if not await self.delete_and_check(ctx):
            return

        role_mention = None
        mention_text = ""

        if ctx.message.reference:
            try:
                replied = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                content = replied.content.lower()
                # First pass: check each word after stripping punctuation
                for word in content.split():
                    cleaned = word.strip(string.punctuation)
                    if cleaned in self.alias_to_role:
                        role_mention = self.alias_to_role[cleaned]
                        break
                # Second pass: regex search for any alias as a whole word
                if not role_mention:
                    for alias, role_name in self.alias_to_role.items():
                        pattern = r'\b' + re.escape(alias) + r'\b'
                        if re.search(pattern, content):
                            role_mention = role_name
                            break
            except Exception:
                pass

        if role_mention:
            role_obj = discord.utils.get(ctx.guild.roles, name=role_mention)
            if role_obj:
                mention_text = f"{role_obj.mention}\n"
            else:
                mention_text = f"@{role_mention}\n"

        output = (
            f"{mention_text}Looking for a group? Make sure to tag the game you're playing and check out the LFG channels!\n"
            "📌 [LFG Guide](https://wiki.mulveycreations.com/discord/lfg)"
        )
        await self.send_reply(ctx, output)

    @commands.command()
    async def host(self, ctx):
        if not await self.delete_and_check(ctx):
            return
        output = (
            "Interested in hosting or promoting something in PA? Check out our guidelines first:\n"
            "📌 [Host/Advertise](https://wiki.mulveycreations.com/servers/hosting)"
        )
        await self.send_reply(ctx, output)

    @commands.command()
    async def biweekly(self, ctx):
        if not await self.delete_and_check(ctx):
            return
        output = (
            "Curious about our biweekly D&D games or need help creating a character? Start here:\n"
            "🧙 [D&D Guide](https://wiki.mulveycreations.com/discord/dnd)"
        )
        await self.send_reply(ctx, output)

    @commands.command()
    async def rule(self, ctx, rule_number: int):
        if not await self.delete_and_check(ctx):
            return

        rules = {
            1: "**1️⃣ Be Respectful**\nTreat everyone respectfully. Disrespectful or toxic behavior will result in action.",
            2: "**2️⃣ 18+ Only**\nPA is for adults only. You must be 18 or older to participate.",
            3: "**3️⃣ Be Civil & Read the Room**\nAvoid sensitive topics unless everyone is comfortable. No such discussions in text channels.",
            4: "**4️⃣ NSFW Content Is Not Allowed**\nExplicit, grotesque, or pornographic content will result in a ban.",
            5: "**5️⃣ Communication - English Preferred**\nPlease speak in English so the whole community can engage.",
            6: "**6️⃣ Use Channels & Roles Properly**\nUse the correct channels for each topic.\n📌 [Roles How-To](https://wiki.mulveycreations.com/discord/roles)\n📌 [LFG Guide](https://wiki.mulveycreations.com/discord/lfg)",
            7: "**7️⃣ Promoting Your Own Content**\nPromote in #promote-yourself or #clip-sharing only. Apply in #applications to post on official PA platforms.",
            8: "**8️⃣ Crowdfunding & Solicitation**\nNo donation or solicitation links allowed. DM spam is not tolerated.",
            9: "**9️⃣ No Unapproved Invites or Links**\nGame server links require vetting and Discord invites are absolutely not allowed.\n📌 [Host/Advertise](https://wiki.mulveycreations.com/servers/hosting)\n📌 [Apply for Vetting](https://discord.com/channels/629113661113368594/693601096467218523/1349427482637635677)",
            10: "**🔟 Build-A-VC Channel Names**\nChannel names must be clean and appropriate for Discord Discovery."
        }

        rule_text = rules.get(rule_number)
        if rule_text:
            embed = discord.Embed(
                title="Full Rules",
                url="https://wiki.mulveycreations.com/rules",
                description=rule_text,
                color=discord.Color.orange()
            )
            await self.send_reply(ctx, embed=embed)
        else:
            await self.send_reply(ctx, "Invalid rule number. Use 1–10.")

    @commands.command()
    async def wow(self, ctx):
        if not await self.delete_and_check(ctx):
            return
        output = (
            "Curious about WoW? Check out the guide here:\n"
            "https://wiki.mulveycreations.com/WoW"
        )
        await self.send_reply(ctx, output)

    @commands.command()
    async def fafo(self, ctx):
        # Only allow users with allowed roles to run the command.
        if not await self.delete_and_check(ctx):
            return
        warning_text = (
            "Warning: If you cannot abide by the rules from previous responses, "
            "Click Below To FAFO"
        )
        view = FafoView()
        await self.send_reply(ctx, warning_text, view=view)

# Required for Redbot compatibility
async def setup(bot):
    await bot.add_cog(Wiki(bot))
