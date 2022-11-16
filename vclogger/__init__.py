from .vclogger import VCLogger

def setup(bot):
    bot.add_cog(VCLogger(bot))