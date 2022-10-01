from .vcalert import VCAlert

def setup(bot):
    bot.add_cog(VCAlert(bot))