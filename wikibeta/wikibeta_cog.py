import discord
import string
import re
from datetime import datetime, timedelta
from redbot.core import commands

class FafoView(discord.ui.View):
    def __init__(self, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.message = None  # Stores the message this view is attached to

    async def on_timeout(self):
        # When the view times out, attempt to delete the message containing it.
        if self.message:
            try:
                await self.message.delete()
            except Exception as e:
                print(f"Failed to delete message on timeout: {e}")

    @discord.ui.button(label="FAFO", style=discord.ButtonStyle.danger)
    async def fafo_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        (Beta) Button callback for FAFO.
        Attempts to timeout the clicking user for 5 minutes using Member.timeout().
        If the member isn't found, or if permissions/HTTP errors occur, an appropriate message is sent.
        """
        await interaction.response.defer(ephemeral=True)
        try:
            duration = timedelta(minutes=5)
            until_time = discord.utils.utcnow() + duration
            # Ensure interaction.user is a Member object; fallback if not found.
            member = interaction.guild.get_member(interaction.user.id)
            if member is None:
                await interaction.followup.send("Member not found.", ephemeral=True)
                return
            await member.timeout(until=until_time, reason="FAFO button clicked.")
            await interaction.followup.send("You have been timed out for 5 minutes.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to timeout you. Please check my role position and permissions.",
                ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"An error occurred while attempting to timeout: {e}", ephemeral=True)

class Wikibeta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Allowed roles for invoking beta commands.
        self.allowed_roles = [
            "Game Server Team", "Advisors", "Wardens", "The Brute Squad", "Sentinels",
            "Community Manager - Helldivers", "Community Manager - Book Club",
            "Community Manager - Call of Duty", "Community Manager - D&D",
            "Community Manager - World of Warcraft", "Community Manager - Minecraft",
            "Skye", "Librarian Raccoon", "Zara", "BadgerSnacks", "Donnie",
            "Captain Sawbones", "Captain Soulo"
        ]
        # Maps common game aliases (all lowercase) to the exact role name.
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
        # Mapping from role names to designated channel IDs (use actual channel IDs).
        self.role_name_to_channel_id = {
            "Escape from Tarkov": 1325558852120350863,
            "Hell Let Loose": 1325565264246603859,
            "Rainbow Six": 1325558740086161428,
            "Ready Or Not": 1325558905907970199,
            "War Thunder": 1325565211884781588,
            "Magic: The Gathering": 1065493485714686003,
            "Pokémon": 1065621451417337956,
            "Table-Top Simulator": 1217529197594021889,
            "Warhammer 40k": 1217529421863456928,
            "Diablo": 1123047882669436958,
            "Path of Exile": 1205575608231530506,
            "Path of Exile 2": 1310386526093578251,
            "Elden Ring": 1315179628993839155,
            "Baldur's Gate 3": 1315180707685073028,
            "Monster Hunter": 1315178720364859402,
            "Final Fantasy": 1328766811671498833,
            "Assetto Corsa": 1315312906178396180,
            "League of Legends": 1308589894268092476,
            "Dota 2": 1308590005911814224,
            "Smite": 1308590072689590374,
            "Marvel Rivals": 1318214983670042707,
            "Overwatch": 1318215028494831697,
            "Phasmophobia": 1328029591062839376,
            "R.E.P.O": 1351009382154109018,
            "Wild Rift": 1316230560946982942,
            "iRacing": 1328799846341148672,
            "Fortnite": 1316416079333167149,
            "Forza": 1328799912892170260
        }
        # Use Discord's internal format for the Channels & Roles clickable link.
        self.channels_and_roles_link = "<id:customize>"

    async def delete_and_check(self, ctx):
        """
        Delete the invoking message and return True if the user is authorized.
        """
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if not any(role.name in self.allowed_roles for role in ctx.author.roles):
            return False
        return True

    async def send_reply(self, ctx, *args, **kwargs):
        """
        Helper to reply to the referenced message if available,
        otherwise sends a new message in the current channel.
        Returns the sent message.
        """
        if ctx.message.reference:
            try:
                original_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                msg = await original_message.reply(*args, **kwargs)
                return msg
            except Exception:
                pass
        msg = await ctx.send(*args, **kwargs)
        return msg

    @commands.command(name="betalfg")
    async def lfg(self, ctx):
        """
        📌 (Beta) Reply to a message to detect game interest and direct users to the correct LFG channel.
        If a game role is detected, the bot will tag the role and provide an LFG guide.
        If used in the wrong channel, the user is informed and directed to grab the game-specific role from <id:customize>.
        """
        if not await self.delete_and_check(ctx):
            return

        role_mention = None
        mention_text = ""
        extra_text = ""

        # Attempt to get role info from the referenced message.
        if ctx.message.reference:
            try:
                replied = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                content = replied.content.lower()
                # First pass: check each word after stripping punctuation.
                for word in content.split():
                    cleaned = word.strip(string.punctuation)
                    if cleaned in self.alias_to_role:
                        role_mention = self.alias_to_role[cleaned]
                        break
                # Second pass: regex search for any alias as a whole word.
                if not role_mention:
                    for alias, role_name in self.alias_to_role.items():
                        pattern = r'\b' + re.escape(alias) + r'\b'
                        if re.search(pattern, content):
                            role_mention = role_name
                            break
            except Exception:
                pass

        if role_mention is None:
            await self.send_reply(ctx, "No game alias detected in the referenced message.")
            return

        # Get the role object.
        role_obj = discord.utils.get(ctx.guild.roles, name=role_mention)
        if role_obj:
            # Default: ping both the role and the user.
            mention_text = f"{role_obj.mention} {ctx.author.mention}\n"
            expected_channel_id = self.role_name_to_channel_id.get(role_obj.name)
            if expected_channel_id:
                if ctx.channel.id == expected_channel_id:
                    # Correct channel: send message in current channel.
                    output = (
                        f"{mention_text}Looking for a group? Make sure to tag the game you're playing and check out the LFG channels!\n"
                        "📌 [LFG Guide](https://wiki.parentsthatga.me/discord/lfg)"
                    )
                    await self.send_reply(ctx, output)
                else:
                    # Wrong channel: inform the user in the current channel.
                    extra_text = (
                        f"Detected game role: **{role_obj.name}**. This is not the correct channel. "
                        f"Please grab the game-specific role from {self.channels_and_roles_link}.\n"
                    )
                    await self.send_reply(ctx, extra_text)
                    # If the user doesn't have the role, assign it.
                    if role_obj not in ctx.author.roles:
                        try:
                            await ctx.author.add_roles(role_obj, reason="User redirected by betalfg command")
                        except Exception as e:
                            print(f"Failed to add role to user: {e}")
                    # Now, in the correct channel, send the LFG message.
                    target_channel = ctx.guild.get_channel(expected_channel_id)
                    if target_channel:
                        output = (
                            f"{role_obj.mention} {ctx.author.mention}\n"
                            "Looking for a group? Make sure to tag the game you're playing and check out the LFG channels!\n"
                            "📌 [LFG Guide](https://wiki.parentsthatga.me/discord/lfg)"
                        )
                        try:
                            await target_channel.send(output)
                        except Exception as e:
                            print(f"Failed to send message in target channel: {e}")
                    else:
                        await self.send_reply(ctx, "Error: Designated channel not found.")
            else:
                # No designated channel mapped: proceed as usual.
                output = (
                    f"{mention_text}Looking for a group? Make sure to tag the game you're playing and check out the LFG channels!\n"
                    "📌 [LFG Guide](https://wiki.parentsthatga.me/discord/lfg)"
                )
                await self.send_reply(ctx, output)
        else:
            await self.send_reply(ctx, f"Could not find role: {role_mention}.")

    @commands.command(name="betahost")
    async def host(self, ctx):
        """
        📣 (Beta) Reply to a message and the bot will link to the hosting/advertising guidelines in PA.
        """
        if not await self.delete_and_check(ctx):
            return
        output = (
            "Interested in hosting or promoting something in PA? Check out our guidelines first:\n"
            "📌 [Host/Advertise](https://wiki.parentsthatga.me/servers/hosting)"
        )
        await self.send_reply(ctx, output)

    @commands.command(name="betabiweekly")
    async def biweekly(self, ctx):
        """
        🧙 (Beta) Reply to a message and this will post info about our biweekly D&D sessions and how to get started.
        """
        if not await self.delete_and_check(ctx):
            return
        output = (
            "Curious about our biweekly D&D games or need help creating a character? Start here:\n"
            "🧙 [D&D Guide](https://wiki.parentsthatga.me/discord/dnd)"
        )
        await self.send_reply(ctx, output)

    @commands.command(name="betarule")
    async def rule(self, ctx, rule_number: int):
        """
        📘 (Beta) Reply to a message and show a quick summary of the selected rule with a link to the full rules page.
        Use: `-betarule 3`
        """
        if not await self.delete_and_check(ctx):
            return
        rules = {
            1: "**1️⃣ Be Respectful**\nTreat everyone respectfully. Disrespectful or toxic behavior will result in action.",
            2: "**2️⃣ 18+ Only**\nPA is for adults only. You must be 18 or older to participate.",
            3: "**3️⃣ Be Civil & Read the Room**\nAvoid sensitive topics unless everyone is comfortable. No such discussions in text channels.",
            4: "**4️⃣ NSFW Content Is Not Allowed**\nExplicit, grotesque, or pornographic content will result in a ban.",
            5: "**5️⃣ Communication - English Preferred**\nPlease speak in English so the whole community can engage.",
            6: "**6️⃣ Use Channels & Roles Properly**\nUse the correct channels for each topic.\n📌 [Roles How-To](https://wiki.parentsthatga.me/discord/roles)\n📌 [LFG Guide](https://wiki.parentsthatga.me/discord/lfg)",
            7: "**7️⃣ Promoting Your Own Content**\nPromote in #promote-yourself or #clip-sharing only. Apply in #applications to post on official PA platforms.",
            8: "**8️⃣ Crowdfunding & Solicitation**\nNo donation or solicitation links allowed. DM spam is not tolerated.",
            9: "**9️⃣ No Unapproved Invites or Links**\nGame server links require vetting and Discord invites are absolutely not allowed.\n📌 [Host/Advertise](https://wiki.parentsthatga.me/servers/hosting)\n📌 [Apply for Vetting](https://discord.com/channels/629113661113368594/693601096467218523/1349427482637635677)",
            10: "**🔟 Build-A-VC Channel Names**\nChannel names must be clean and appropriate for Discord Discovery."
        }
        rule_text = rules.get(rule_number)
        if rule_text:
            embed = discord.Embed(
                title="Full Rules",
                url="https://wiki.parentsthatga.me/rules",
                description=rule_text,
                color=discord.Color.orange()
            )
            await self.send_reply(ctx, embed=embed)
        else:
            await self.send_reply(ctx, "Invalid rule number. Use 1–10.")

    @commands.command(name="betawow")
    async def wow(self, ctx):
        """
        🐉 (Beta) Reply to a message and this will link to the World of Warcraft wiki section for PA players.
        """
        if not await self.delete_and_check(ctx):
            return
        output = (
            "Curious about WoW? Check out the guide here:\n"
            "https://wiki.parentsthatga.me/WoW"
        )
        await self.send_reply(ctx, output)

    @commands.command(name="betafafo")
    async def fafo(self, ctx):
        """
        ⚠️ (Beta) Under development. Posts a warning message and a 'FAFO' button.
        Users who click it are timed out for 5 minutes.
        """
        if not await self.delete_and_check(ctx):
            return
        warning_text = (
            "Warning: If you cannot abide by the rules from previous responses, "
            "Click Below To FAFO"
        )
        view = FafoView()
        msg = await self.send_reply(ctx, warning_text, view=view)
        view.message = msg

async def setup(bot):
    await bot.add_cog(Wikibeta(bot))
