from .musicrestricter import MusicRestricter

def setup(bot):
    bot.add_cog(MusicRestricter(bot))