import asyncio
import discord
from redbot.core import commands
from redbot.core.config import Config
import os
import json
from bs4 import BeautifulSoup
import requests
import aiohttp
import moviepy.editor as mpe
from moviepy.video.io.ffmpeg_tools import *

#from pystreamable import StreamableApi
from .utils import sanitize
#import flickr_api
from async_gfycat.client import GfycatClient

class Redditparser(commands.Cog):
    """The Reddit parser cog"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=718395193090375700, force_registration=True)

        default_guild = {
            "state": True,
            "ignoreusers": False,
            "ignorebots": True,
            "channels": [941030171769712750, 1004709931661938738, 1004709989971144754],
        }

        default_global = {
            "gfycat_id": "2_3H0ssg",
            "gfycat_secret": "uHzN9K5CHKmQ80admmva5JXITj9W5DE-FTcLIz9dcxn_S6Fn3c4EVsArBIZZ-uBo"        
        }

        self.config.register_guild(**default_guild)
        self.config.register_guild(**default_global)

    async def upload_media(self, media, title):
        
        #client_id = await self.config.gfycat_id()
        #client_secret = await self.config.gfycat_secret()
        clientid = "2_3H0ssg"
        clientsecret = "uHzN9K5CHKmQ80admmva5JXITj9W5DE-FTcLIz9dcxn_S6Fn3c4EVsArBIZZ-uBo"

        client = GfycatClient(clientid, clientsecret)

        code = await client.upload_from_file(media, title=title)

        await asyncio.sleep(60)

        try:
            data = await client.query_gfy(code)
            
        except:
            await asyncio.sleep(240)
            data = await client.query_gfy(code)

        print(data["gfyItem"]['content_urls']['100pxGif']['largeGif'])
        return data["gfyItem"]['content_urls']['100pxGif']['largeGif']['url']


        #FUCKING POST THE URL DICKHEAD

    def message_parser(self, message):
        redditlinks = []
        print(message)
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
        print("Image func is run")     
        image = json_data['posts']['models'][post_id]['media']['content']
        title = json_data['posts']['models'][post_id]['title']
        author = json_data['posts']['models'][post_id]['author'] 
        isnsfw = json_data['posts']['models'][post_id]['isNSFW']
        spoiler = json_data['posts']['models'][post_id]['isSpoiler']
        flair = json_data['posts']['models'][post_id]['flair']
        upvoteRatio = json_data['posts']['models'][post_id]['upvoteRatio']
        permalink = json_data['posts']['models'][post_id]['permalink']

        embed=discord.Embed(description=f"**[{title}]({permalink})**",color=discord.Color.random())        
        embed.add_field(name=f"Author:", value=f"u/{author}", inline=False)
        embed.add_field(name="Upvote Ratio:", value=f"{upvoteRatio}", inline=False)
        embed.set_image(url=image)

        if spoiler == True:
            content = f"|| <{image}> ||"
        else:
            content = f"<{image}>"
        
        if ctx.channel.is_nsfw() == True: 
            await ctx.send(content=content, embed=embed)
        else:
            if isnsfw == True:
                await ctx.send("This post is NSFW, please use this command in a NSFW channel.")
        

    #Broken right now, needs to be fixed
    async def get_text(self, ctx, json_data, post_id):
        document = json_data['posts']['models'][post_id]['media']['richtextContent']['document'][0]
        print(document)
        text = ""
        #await ctx.send(document['c'][0]['t'])
        try:
            for i in document:
                text = text + i['c'][0]['t'] + "\n"

        except:
            text = document['c'][0]['t'] 

        await ctx.send(content=text)

    async def get_gif(self, ctx, json_data, post_id):
        print("gif function is run")
        global path
        path = 'D:\\Red-Cogs\\redditparser\\'
        headers = {'User-Agent':'Mozilla/5.0'}

        gif = json_data['posts']['models'][post_id]['media']['content']
        title = json_data['posts']['models'][post_id]['title']
        filename = sanitize(title)

        title = json_data['posts']['models'][post_id]['title']
        author = json_data['posts']['models'][post_id]['author'] 
        isnsfw = json_data['posts']['models'][post_id]['isNSFW']
        spoiler = json_data['posts']['models'][post_id]['isSpoiler']
        flair = json_data['posts']['models'][post_id]['flair']
        upvoteRatio = json_data['posts']['models'][post_id]['upvoteRatio']
        permalink = json_data['posts']['models'][post_id]['permalink']

        embed=discord.Embed(description=f"**[{title}]({permalink})**",color=discord.Color.random())        
        embed.add_field(name=f"Author:", value=f"u/{author}", inline=False)
        embed.add_field(name="Upvote Ratio:", value=f"{upvoteRatio}", inline=False)

        with open(path + f'{filename}.mp4','wb') as file:
            response = requests.get(gif,headers=headers)
            if(response.status_code == 200):
                file.write(response.content)
                file.close()
            else:
                file.close()

        assert os.path.isfile(path + f'{filename}.mp4')
        file=discord.File(path + f'{filename}.mp4')
        
        await ctx.send(embed=embed, file=file)
        os.remove(path + f'{filename}.mp4')

    async def get_video(self, ctx, json_data, post_id):
        path = 'D:\\Red-Cogs\\redditparser\\'
        headers = {'User-Agent':'Mozilla/5.0'}
        print("video function is run")
        title = json_data['posts']['models'][post_id]['title']
        filename = sanitize(title)
        
        dash_url = json_data['posts']['models'][post_id]['media']['dashUrl']
        height  = json_data['posts']['models'][post_id]['media']['height']
        dash_url = dash_url[:int(dash_url.find('DASH')) + 4]
        video_url = f'{dash_url}_{height}.mp4'
        audio_url = f'{dash_url}_audio.mp4'

        with open(path + f'{filename}_video.mp4','wb') as file:
            response = requests.get(video_url,headers=headers)
            if(response.status_code == 200):
                file.write(response.content)
                file.close()
            else:
                file.close()

        with open(path + f'{filename}_audio.mp3','wb') as file:
            response = requests.get(audio_url,headers=headers)
            if(response.status_code == 200):
                file.write(response.content)
                file.close()
            else:
                file.close()

        def combine_audio(vidname, audname, outname):
            ffmpeg_merge_video_audio(vidname, audname, outname, vcodec='copy', acodec='copy', ffmpeg_output=False, logger=None)

        assert os.path.isfile(path + f'{filename}_video.mp4')
        assert os.path.isfile(path + f'{filename}_audio.mp3')
        
        try:
            combine_audio(path + f'{filename}_video.mp4', path + f"{filename}_audio.mp3", path + f"{filename}.mp4")

            file=discord.File(path + f'{filename}.mp4')

            os.remove(path + f"{filename}_video.mp4")
            os.remove(path + f"{filename}_audio.mp3")

            pathtovideo= "D:\\Red-Cogs\\redditparser\\" + filename + ".mp4"


            if os.stat(pathtovideo).st_size < 8000000:
                await ctx.send(file=file)
                os.remove(path + f"{filename}.mp4")

            else:
                url = await self.upload_media(pathtovideo, filename)
                os.remove(path + f"{filename}.mp4")

        except:
            try:
                os.remove(path + f"{filename}_audio.mp3")
            except:
                pass

            file=discord.File(path + f'{filename}_video.mp4')


            pathtovideo= "D:\\Red-Cogs\\redditparser\\" + filename + "_video.mp4"


            if os.stat(pathtovideo).st_size < 8000000:
                await ctx.send(file=file)
                os.remove(path + f"{filename}._video.mp4")

            else:
                url = await self.upload_media(pathtovideo, filename)
                os.remove(path + f"{filename}._video.mp4")      



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
                
                title = json_data['posts']['models'][post_id]['title']
                filename = sanitize(title)

                author = json_data['posts']['models'][post_id]['author'] 
                #dash_url = json_data['posts']['models'][post_id]['media']['dashUrl']
                #height  = json_data['posts']['models'][post_id]['media']['height']
                isnsfw = json_data['posts']['models'][post_id]['isNSFW']
                spoiler = json_data['posts']['models'][post_id]['isSpoiler']
                flair = json_data['posts']['models'][post_id]['flair']
                upvoteRatio = json_data['posts']['models'][post_id]['upvoteRatio']

                #try:
                type = json_data['posts']['models'][post_id]['media']['type']

                if type == "image":
                    print("Image")
                    await self.get_image(ctx, json_data, post_id)
                if type == "gifvideo":
                    print("Gif")
                    await self.get_gif(ctx, json_data, post_id)
                if type == "video":
                    print("Video")
                    await self.get_video(ctx, json_data, post_id)
                if type == "rtjson":
                    print("RTJSON")
                    await self.get_text(ctx, json_data, post_id)
                #except:
                #    try:
                #        source = json_data['posts']['models'][post_id]['source']['url']
                #        if source != None:
                #            await ctx.send(source)
                #    except:
                #        pass

        await session.close()

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
        #check for duplicates

        guild_group = self.config.guild(ctx.guild)
        async with guild_group.channels() as channels:
            channels.append(channelID)

        await ctx.send(f"Reddit links will now be parsed in <#{channelID}>")

    @commands.is_owner()
    @rpsettings.command()
    async def removechannel(self, ctx, *, channelID:int):
        """
        This command adds a channel to the list of channels to parse
        """
        #check if it isnt here 
        guild_group = self.config.guild(ctx.guild)
        async with guild_group.channels() as channels:
            channels.remove(channelID)

        await ctx.send(f"Reddit links will no longer be parsed in <#{channelID}>")
            
