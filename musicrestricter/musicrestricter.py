import discord
from redbot.core import commands
from redbot.core import Config  

class MusicRestricter(commands.Cog):
    """A cog to stop multiple music bots from playing at once"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=718395193090375700, force_registration=True)

        default_guild = {
            "state": True,
            "channels": [],
            "musicbots": []        
        }

        self.config.register_guild(**default_guild)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        state = await self.config.guild(member.guild).state()
        channels = await self.config.guild(member.guild).channels()
        musicbots = await self.config.guild(member.guild).musicbots()
        number_of_bots = 0

        if not state:
            return

        if member.bot == False:
            return

        if channels == []:
            return

        if before.channel is None and after.channel is not None:
            if after.channel.id in channels:
                for musicbot in musicbots:
                    for i in after.channel.members:
                        if i.id == musicbot:
                            number_of_bots += 1
        
        if number_of_bots > 1:
            await member.move_to(None)

