import discord
from redbot.core import commands
from redbot.core import Config

class VCLogger(commands.Cog):
    """A VCLogger cog"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=718395193090375700, force_registration=True)

        default_guild = {
            "state": True,
            "logchannel": None,
            "join_msg": "{member.mention} joined the vc",
            "leave_msg": "{member.mention} left the vc",
        }

        self.config.register_guild(**default_guild)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        join_msg = await self.config.guild(member.guild).join_msg()
        leave_msg = await self.config.guild(member.guild).leave_msg()
        logchannel = await self.config.guild(member.guild).logchannel()
        state = await self.config.guild(member.guild).state()

        if not state:
            return

        if logchannel is None:
            return

        if before.channel is None and after.channel is not None:
            try: 
                channel = self.bot.get_channel(logchannel)
                if "{member.mention}" in join_msg:
                    await channel.send(join_msg.format(member=member))
                elif join_msg != "":
                    await channel.send(join_msg)
            except:
                return

        elif before.channel is not None and after.channel is None:
            try:
                channel = self.bot.get_channel(logchannel)
                if "{member.mention}" in leave_msg:
                    await channel.send(leave_msg.format(member=member))
                elif leave_msg != "":
                    await channel.send(leave_msg)
                else:
                    return
            except:
                return

    @commands.group(name="vcls")
    @commands.is_owner()
    async def vcloggersettings(self, ctx):
        """
        Settings for the VC Logger cog
        """
        pass

    @vcloggersettings.command(name="state")
    @commands.is_owner()
    async def vcloggersettings_state(self, ctx, state: bool):
        """
        Toggle the state of the VC Logger cog
        """
        await self.config.guild(ctx.guild).state.set(state)
        await ctx.send(f"VC Logger state set to {state}")

    @vcloggersettings.command(name="logchannel")
    @commands.is_owner()
    async def vcloggersettings_logchannel(self, ctx, channel: int):
        """
        Set the log channel for the VC Logger cog
        """
        await self.config.guild(ctx.guild).logchannel.set(channel)
        await ctx.send(f"VC Logger log channel set to <#{channel}>")

    @vcloggersettings.command(name="joinmsg")
    @commands.is_owner()
    async def vcloggersettings_joinmsg(self, ctx, *, msg: str):
        """
        Set the join message for the VC Logger cog
        """
        await self.config.guild(ctx.guild).join_msg.set(msg)
        await ctx.send(f"VC Logger join message set to {msg}")

    @vcloggersettings.command(name="leavemsg")
    @commands.is_owner()
    async def vcloggersettings_leavemsg(self, ctx, *, msg: str):
        """
        Set the leave message for the VC Logger cog
        """
        await self.config.guild(ctx.guild).leave_msg.set(msg)
        await ctx.send(f"VC Logger leave message set to {msg}")

    