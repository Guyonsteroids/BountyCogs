from .diceroller import DiceRoller

def setup(bot):
    bot.add_cog(DiceRoller(bot))