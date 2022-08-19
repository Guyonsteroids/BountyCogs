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

                    alert_message = f"\n{member.name} has joined {after.channel.name}\n{member.mention} - UserID: {member.id} - Voice channel: {after.channel.name}\n\n{peopletoping}"
                    
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
    async def add(self, ctx, ids: Greedy[int] = None):
        """
        Adds user IDs to the alert list
        """
        guild_group = self.config.guild(ctx.guild)
        embed=discord.Embed(color=discord.Color.random())
        if ids is None:
            embed.add_field(name=f"Failed", value=f"No IDs provided")
            await ctx.send(embed=embed)
        else:
            for id in ids:
                async with guild_group.alert_list() as alert_list:
                    alert_list.append(id)
                    alert_list = [*set(alert_list)] # filter duplicates
                    
            embed.add_field(name=f"Success:", value=f"{ids} Added to alert list")
            await ctx.send(embed=embed)

    @vcalert.command()
    async def remove(self, ctx, ids: Greedy[int]):
        """
        Removes user IDs from the alert list
        """
        guild_group = self.config.guild(ctx.guild)
        success = []
        failed=[]
        embed=discord.Embed(color=discord.Color.random())
        for id in ids:
            async with guild_group.alert_list() as alert_list:
                try:
                    alert_list.remove(id)
                    success.append(id)
                except:
                    failed.append(id)
                    failed = [*set(failed)] # filter duplicates
        if len(success) > 0:
            embed.add_field(name="Success:", value=f"{success} removed from the alert list")

        if len(failed) > 0:
            embed.add_field(name="Failed:", value=f"Failed to remove {failed} from the alert list. Please try again")
        
        await ctx.send(embed=embed)

    @vcalert.command()
    async def list(self, ctx):
        """
        Lists the user IDs in the alert list
        """
        alert_list = await self.config.guild(ctx.guild).alert_list()
        alert_list = [*set(alert_list)]
        if alert_list == []:
            alert_list = "No IDs in the alert list"
        embed=discord.Embed(title="Alert List:", description=f"{alert_list}", color=discord.Color.random())
        
        await ctx.send(embed=embed)

    @vcalert.command()
    async def padd(self, ctx, ids: Greedy[int] = None):
        """
        Adds user IDs to the ping list
        """
        guild_group = self.config.guild(ctx.guild)
        embed=discord.Embed(color=discord.Color.random())

        if ids == None:
            async with guild_group.ping_list() as ping_list:
                ids=ctx.author.id
                ping_list.append(ids)
                ping_list = [*set(ping_list)] # filter duplicates
                
        else:
            for id in ids:
                async with guild_group.ping_list() as ping_list:
                    ping_list.append(id)
                    ping_list = [*set(ping_list)] # filter duplicates
                    
        embed.add_field(name="Success:", value=f"{ids} added to the ping list")

        await ctx.send(embed=embed)

    @vcalert.command()
    async def premove(self, ctx, ids: Greedy[int] = None):
        """
        Removes user IDs from the ping list
        """
        guild_group = self.config.guild(ctx.guild)
        success=[]
        failed=[]
        embed=discord.Embed(color=discord.Color.random())
        if ids == None:
            async with guild_group.ping_list() as ping_list:
                ids=ctx.author.id
                try:
                    ping_list.remove(ids)
                    success.append(ids)
                except:
                    failed.append(ids)
                    failed = [*set(failed)] # filter duplicates

        else:
            for id in ids:
                async with guild_group.ping_list() as ping_list:
                    try:
                        ping_list.remove(id)
                    except:
                        failed.append(id)
                        failed = [*set(failed)] # filter duplicates
                        
        if len(success) > 0:
            embed.add_field(name="Success:", value=f"{success} removed from the ping list")

        if len(failed) > 0:
            embed.add_field(name="Failed:", value=f"Failed to remove {failed} from the ping list. Please try again")
        
        await ctx.send(embed=embed)
        

    @vcalert.command()
    async def plist(self, ctx):
        """
        Lists the user IDs in the ping list
        """
        ping_list = await self.config.guild(ctx.guild).ping_list()
        ping_list = [*set(ping_list)]
        if ping_list == []:
            ping_list = "No IDs in the alert list"
        embed=discord.Embed(title="Ping List:", description=f"{ping_list}", color=discord.Color.random())
        await ctx.send(embed=embed)   

    @vcalert.command()
    async def logchannel(self, ctx, channel: int = None):
        """
        Set the log channel for the VC Alert cog
        """
        if channel is None:
            await ctx.send(f"VC Alert is currently logging to <#{channel}>")
        else:
            await self.config.guild(ctx.guild).logchannel.set(channel)
            await ctx.send(f"VC Alert log channel set to <#{channel}>")
