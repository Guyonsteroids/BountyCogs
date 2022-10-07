class Redditparser(commands.Cog):
    """The Reddit parser cog"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=718395193090375700, force_registration=True)

        default_guild = {
            "state": True,
            "ignoreusers": False,
            "ignorebots": True,
            "channels": [],
        }

        default_global = {
            "mail": "",
            "password": ""     
        }

        self.config.register_guild(**default_guild)
        self.config.register_guild(**default_global)

    def message_parser(self, message):
        redditlinks = []
        words = message.split()
        for word in words:
            if "reddit.com/r/" in word:
                link = "https://www.reddit.com/r/" + word.split("reddit.com/r/", maxsplit=2)[1] # this is to prevent old.reddit links or other links from breaking the bot
                redditlinks.append(link)
            else:
                pass
            
        redditlinks = list(set(redditlinks)) # filters duplicates

        if redditlinks == []:
            return None
        else: 
            return redditlinks

    async def get_image(self, ctx, json_data, post_id):   

        image = json_data['posts']['models'][post_id]['media']['content']
        title = json_data['posts']['models'][post_id]['title']
        author = json_data['posts']['models'][post_id]['author']
        subbreddit = json_data['posts']['models'][post_id]['subreddit']['name']
        spoiler = json_data['posts']['models'][post_id]['isSpoiler']
        permalink = json_data['posts']['models'][post_id]['permalink']


        embed=discord.Embed(description=f"**[{title}]({permalink})**",color=discord.Color.random())        
        embed.add_field(name=f"Author:", value=f"u/{author}", inline=True)
        embed.add_field(name=f"Subreddit:", value=f"r/{subbreddit}", inline=True)
        embed.set_image(url=image)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

        if spoiler == True:
            content = f"|| <{image}> ||"
        else:
            content = f"<{image}>"

        await ctx.send(content=content, embed=embed)

    async def get_text(self, ctx, json_data, post_id):
        document = json_data['posts']['models'][post_id]['media']['richtextContent']['document'][0]

        title = json_data['posts']['models'][post_id]['title']
        author = json_data['posts']['models'][post_id]['author']
        subbreddit = json_data['posts']['models'][post_id]['subreddit']['name']
        permalink = json_data['posts']['models'][post_id]['permalink']
        text=document['c'][0]['t']

        embed=discord.Embed(description=f"**[{title}]({permalink})**\n{text[0:4000] }",color=discord.Color.random())        
        embed.add_field(name=f"Author:", value=f"u/{author}", inline=True)
        embed.add_field(name=f"Subreddit:", value=f"r/{subbreddit}", inline=True)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    async def get_post(self, ctx, url):
        headers = {'User-Agent':'Mozilla/5.0'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:

                post_id = url[url.find('comments/') + 9:]
                post_id = f"t3_{post_id[:post_id.find('/')]}"
                text= await resp.text()

                soup = BeautifulSoup(text,'lxml')
                required_js = soup.find('script',id='data')
                json_data = json.loads(required_js.text.replace('window.___r = ','')[:-1])

                nsfw = json_data['posts']['models'][post_id]['isNSFW']
                try:
                    type = json_data['posts']['models'][post_id]['media']['type']
                except:
                    type = url

                if ctx.channel.is_nsfw() or not nsfw: 
                    print(type)
                    if type == "image":
                        await self.get_image(ctx, json_data, post_id)
                    if type == "rtjson":
                        print("RTJSON")
                        await self.get_text(ctx, json_data, post_id)
                        
                else:    
                    await ctx.send("This post is NSFW, please use this command in a NSFW channel.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ctx = await self.bot.get_context(message)
        channels = await self.config.guild(ctx.guild).channels()
        
        if message.guild is None:
            return
        
        if message.author == self.bot.user:
            return

        if message.channel.id not in channels:
            return

        if "reddit.com/r/" not in message.content:
            return

        else:
            links = self.message_parser(message.content)
        
            if links is not None:
                for link in links:
                    await self.get_post(ctx, link)


    #SETTINGS
    @commands.is_owner()
    @commands.group()
    async def rpsettings(self, ctx):
        """
        This settings for the redditparser cog
        """
        pass

    @commands.is_owner()
    @rpsettings.command()
    async def state(self, ctx, state:bool):
        """
        This command enables or disables the redditparser cog
        """
        await self.config.guild(ctx.guild).state.set(state)
        await ctx.send("State set to {}".format(state))

    @commands.is_owner()
    @rpsettings.command()
    async def ignoreusers(self, ctx, state:bool):
        """
        This command enables or disables link parsing for users
        """
        await self.config.guild(ctx.guild).ignoreusers.set(state)
        await ctx.send("Ignoreusers set to {}".format(state))

    @commands.is_owner()
    @rpsettings.command()
    async def ignorebots(self, ctx, state:bool):
        """
        This command enables or disables link parsing for bots
        """
        await self.config.guild(ctx.guild).ignorebots.set(state)
        await ctx.send("Ignorebots set to {}".format(state))    

    @commands.is_owner()
    @rpsettings.command()
    async def addchannel(self, ctx, *, channelID:int):
        """
        This command adds a channel to the list of channels to parse
        """
        guild_group = self.config.guild(ctx.guild)
        async with guild_group.channels() as channels:
            if channelID in channels:
                await ctx.send("Channel already in list")
            else:
                channels.append(channelID)
                await ctx.send(f"Reddit links will now be parsed in <#{channelID}>")

    @commands.is_owner()
    @rpsettings.command()
    async def removechannel(self, ctx, *, channelID:int):
        """
        This command adds a channel to the list of channels to parse
        """
        guild_group = self.config.guild(ctx.guild)
        async with guild_group.channels() as channels:
            if channelID not in channels:
                await ctx.send("Channel not in list")
            else:
                channels.remove(channelID)
                await ctx.send(f"Reddit links will no longer be parsed in <#{channelID}>")

