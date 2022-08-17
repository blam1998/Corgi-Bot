import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import asyncio


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.isPlaying = False
        self.donePlaying = False

        #2D list containing [Song, Channel]

        self.musicQueue = []
        self.ydlOptions = {'format':'bestaudio', 'noplaylist':'True'}
        self.ffmpegOptions = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = ""
        self.musicLoop = ""

    def search_youtube(self,item):
        #With statement ensures proper acquisition and release of resources.

        with YoutubeDL(self.ydlOptions) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download = False)['entries'][0]
            except Exception:
                return False
        #Info is returned as a nested dictionary and we're pulling data from it.

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.musicQueue) > 0:
            self.isPlaying = True
            print("play next")

            m_url = self.musicQueue[0][0]['source']

            self.musicQueue.pop(0)
            #test = asyncio.run_coroutine_threadsafe(self.play_next(), self.musicLoop)
            if not self.vc.is_playing():
                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.ffmpegOptions), after=lambda e: self.play_next())

        else:
            self.isPlaying = False

    async def play_music(self):
        if len(self.musicQueue) > 0:
            self.isPlaying = True

            m_url = self.musicQueue[0][0]['source']

            #make sure we're connected to a voice channel
            #bot needs to know what channel to join.
            if self.vc == "" or not self.vc.is_connected():
                self.vc = await self.musicQueue[0][1].connect()

            self.musicQueue.pop(0)
            #test = asyncio.run_coroutine_threadsafe(self.play_next(), self.musicLoop)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.ffmpegOptions), after=lambda e: self.play_next())
            print("Done Playing")

        else:
            self.isPlaying = False

    @commands.command()
    async def play(self, ctx, *args):
        #context is used to tell what channel user sent the message from
        query = " ".join(args)

        if ctx.author.voice is None:
            await ctx.send("Please connect to a voice channel before playing music")
        else:
            voiceChannel = ctx.author.voice.channel

            song = self.search_youtube(query)

            if type(song) == type(True):
                await ctx.send("Please try another URL")
            else:
                await ctx.send("Song added to the queue")
                self.musicQueue.append([song,voiceChannel])

            if self.isPlaying == False:
                self.musicLoop = asyncio.new_event_loop()
                await self.play_music()

    @commands.command()
    async def queue(self, context):
        returnVal = ""
        for i in range(0,len(self.musicQueue)):
            returnVal += self.musicQueue[i][0]['title'] + "\n"

        print(returnVal)
        if returnVal != "":
            await context.send(returnVal)
        else:
            await context.send("No music in queue")

    #stop current song and plays the next song
    @commands.command()
    async def skip(self,ctx):
        if self.vc != "":
            self.vc.stop()
            await ctx.send("Skipping song")
            await self.play_music()
        else:
            await self.play_music()

    @commands.command()
    async def leave(self,ctx):
        await self.vc.disconnect()
        self.vc = ""
        self.isPlaying = False

    #need to implement a bot move command, so user can move the bot to the channel they want. (2)
def setup(client):
    client.add_cog(Music(client));