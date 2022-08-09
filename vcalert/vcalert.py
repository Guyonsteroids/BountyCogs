import discord
from redbot.core import commands
from redbot.core import Config
from discord.ext.commands import Greedy

class VCAlert(commands.Cog):
    """VCAlert cog"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=718395193090375700, force_registration=True)

        default_guild = {
            "state": True,
            "alert_list": [],
            "ping_list": [],
            "logchannel": None,
        }

        self.config.register_guild(**default_guild)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        logchannel = self.bot.get_channel(await self.config.guild(member.guild).logchannel())
        state = await self.config.guild(member.guild).state()
        alert_list = await self.config.guild(member.guild).alert_list()
        ping_list = await self.config.guild(member.guild).ping_list()
        
        if not state:
            return

        if logchannel is None:
            return

        if before.channel is None and after.channel is not None:
            try: 
                if member.id in alert_list:
                    peopletoping = ""
                    for id in ping_list:
                        peopletoping += f"<@{id}> "

                    alert_message = f"{member.name} has joined {after.channel.name}\n{peopletoping} - {member.id} - {after.channel.mention}                    "
                    
                    await logchannel.send(alert_message)

            except:
                return

    @commands.group()
    async def vcalert(self, ctx):
        """
        Settings for the VC Alert cog
        """
        pass

    @vcalert.command()
    async def state(self, ctx, state: bool):
        """
        Toggle the state of the VC Alert cog
        """
        await self.config.guild(ctx.guild).state.set(state)
        await ctx.send(f"VC Alert state set to {state}")

    @vcalert.command()
    async def add(self, ctx, ids: Greedy[int]):
        """
        Adds user IDs to the alert list
        """
        guild_group = self.config.guild(ctx.guild)
        for id in ids:
            async with guild_group.alert_list() as alert_list:
                alert_list.append(id)
                alert_list = list(set(alert_list)) # filter duplicates

        await ctx.send(f"{ids} added to the alert list")

    @vcalert.command()
    async def remove(self, ctx, ids: Greedy[int]):
        """
        Removes user IDs from the alert list
        """
        guild_group = self.config.guild(ctx.guild)
        failed=[]
        for id in ids:
            async with guild_group.alert_list() as alert_list:
                try:
                    alert_list.remove(id)
                except:
                    failed.append(id)
                    failed = list(set(failed)) # filter duplicates
        
        await ctx.send(f"{ids} removed from the alert list\nFailed to remove {failed}. Please try again")

    @vcalert.command()
    async def list(self, ctx):
        """
        Lists the user IDs in the alert list
        """
        alert_list = await self.config.guild(ctx.guild).alert_list()
        await ctx.send(f"{alert_list}")

    @vcalert.command()
    async def padd(self, ctx, ids: Greedy[int]):
        """
        Adds user IDs to the ping list
        """
        guild_group = self.config.guild(ctx.guild)

        if ids == "":
            async with guild_group.ping_list() as ping_list:
                ping_list.append(ctx.author.id)
                ping_list = list(set(ping_list)) # filter duplicates
        
        else:
            for id in ids:
                async with guild_group.ping_list() as ping_list:
                    ping_list.append(id)
                    ping_list = list(set(ping_list)) # filter duplicates

        await ctx.send(f"{ids} added to the ping list")

    @vcalert.command()
    async def premove(self, ctx, ids: Greedy[int]):
        """
        Removes user IDs from the ping list
        """
        guild_group = self.config.guild(ctx.guild)
        failed=[]
        if ids == "":
            async with guild_group.ping_list() as ping_list:
                try:
                    ping_list.remove(ctx.author.id)
                except:
                    failed.append(ctx.author.id)
                    failed = list(set(failed)) # filter duplicates

        else:
            for id in ids:
                async with guild_group.ping_list() as ping_list:
                    try:
                        ping_list.remove(id)
                    except:
                        failed.append(id)
                        failed = list(set(failed)) # filter duplicates
        
        await ctx.send(f"{ids} removed from the ping list\nFailed to remove {failed}. Please try again")

    @vcalert.command()
    async def plist(self, ctx):
        """
        Lists the user IDs in the ping list
        """
        ping_list = await self.config.guild(ctx.guild).ping_list()
        await ctx.send(f"{ping_list}")   

    @vcalert.command()
    async def logchannel(self, ctx, channel: int):
        """
        Set the log channel for the VC Alert cog
        """
        if channel is None:
            await self.config.guild(ctx.guild).logchannel.set(None)
            await ctx.send("Log channel set to None")
        else:
            await self.config.guild(ctx.guild).logchannel.set(channel)
            await ctx.send(f"VC Alert log channel set to <#{channel}>")

    
    
        
        

        
    

    