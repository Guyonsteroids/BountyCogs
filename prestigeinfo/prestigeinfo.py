import discord
from redbot.core import commands

class Prestigeinfo(commands.Cog):
    """Prestigeinfo cog"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def prestigeinfo(self, ctx, prestigelevel: int = 1):
        """Get information about prestige"""
        embed=discord.Embed(title=f"Prestige {prestigelevel}", color=discord.Color.random())
        coin_requirement = 4500000 * prestigelevel
        if coin_requirement > 250000000:
            coin_requirement = 250000000
        level_requirement = 20 * prestigelevel
        inventory_requirement = 35000000 * prestigelevel

        donor_coin_requirement = 3500000 * prestigelevel
        if donor_coin_requirement > 250000000:
            donor_coin_requirement = 250000000
        donor_level_requirement = 15 * prestigelevel
        donor_inventory_requirement = 25000000 * prestigelevel
        embed.add_field(name="Non-Donor Requirements:", value=f"Coin Requirements: {coin_requirement}\nLevel Requirement: {level_requirement}\nInventory Worth: {inventory_requirement}", inline=False)
        embed.add_field(name="Donor Requirements:", value=f"Coin Requirements: {donor_coin_requirement}\nLevel Requirement: {donor_level_requirement}\nInventory Worth: {donor_inventory_requirement}", inline=False)
        embed.set_footer(text="Run `/prestige` to prestige | Made by HellFire#7769")
        await ctx.send(embed=embed)

    @commands.command()
    async def omegaprestigeinfo(self, ctx, omegalevel: int = 1):
        """Get information about omega prestige"""
        if omegalevel > 25:
          await ctx.send("Omega prestige is capped at level 25")
          return
          
        def coinreq(omegalevel):
            return 100000000 * omegalevel

        def calcprestige(x):
          return 1+(2*x)

        def total_prestige(n):
          ans = 0
          for i in range(1,n+1,1):
            ans += calcprestige(i)
          return ans

        def calc_levels_per_prestige(x):
          ans = 0
          max_prestige_no = 1+(2*x)
          for i in range(1, max_prestige_no+1, 1): #loop to calculate     levels for every prestige level
            ans += 20*i
          return ans

        omegalevel=5
        ans = 0
        for i in range(1,omegalevel+1,1): #loop for every omega level
          ans += calc_levels_per_prestige(i)
        
        embed=discord.Embed(title=f"Omega Prestige {omegalevel}", color=discord.Color.random())
        embed.add_field(name="Omega Level Requirements:", value=f"\nTotal Level Requirements: {ans}\nTotal Prestige: {total_prestige(omegalevel)}\nTotal Coin Requirement: {coinreq(omegalevel)}", inline=False)

        await ctx.send(embed=embed)
   