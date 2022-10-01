from .redditparser import Redditparser

def setup(bot):
    bot.add_cog(Redditparser(bot))