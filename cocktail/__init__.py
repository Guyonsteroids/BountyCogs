from .cocktail import Cocktail

def setup(bot):
    bot.add_cog(Cocktail(bot))