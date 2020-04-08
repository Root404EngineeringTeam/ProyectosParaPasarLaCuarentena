import os
import hashlib
import discord
import youtube_dl
import asyncio

from async_timeout import timeout
from requests import get
from bs4 import BeautifulSoup


class MusicQueue():

    def __init__(self, channel, loop):
        self.queue = asyncio.Queue(maxsize=10)
        self.next = asyncio.Event()

        self.channel = channel
        self.loop = loop

        self.task = self.loop.create_task(self.queue_worker())
        self.active = True

    def destroy(self):
        self.active = False
        self.task.cancel()

    async def queue_worker(self):
        while self.active:
            self.next.clear()

            try:
                async with timeout(300):
                    source = await self.queue.get()

            except asyncio.TimeoutError:
                self.destroy()

            if not self.channel.is_connected():
                self.destroy()

            self.channel.play(source, after=lambda _: self.loop.call_soon_threadsafe(self.next.set))
            self.channel.is_playing()

            await self.next.wait()

            source.cleanup()


class MusicPlayer():

    def __init__(self):
        self.queues = {}

    async def get_voice_channel(self, client, author):
        voice_channel = discord.utils.get(client.voice_clients, guild=author.guild)

        if not voice_channel or not voice_channel.is_connected():
            if not author.voice:
                return False

            voice_channel = await author.voice.channel.connect()

        return voice_channel

    def search_yt_video(self, query):
        response = get("https://www.youtube.com/results?search_query=%s" %(query))

        soup = BeautifulSoup(response.text, 'lxml')

        videos = []
        for vid in soup.find_all(attrs={'class':'yt-uix-tile-link'}, limit=10):
            url = 'https://www.youtube.com' + vid['href']
            name = vid['title']

            videos.append({'url':url, 'name':name})

        return videos

    def download_yt_video(self, url):
        response = get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        song_filename = soup.find("meta", attrs={'property':'og:title'})['content']
        song_filename = "songs/%s.mp3" %(song_filename)

        if not os.path.exists(song_filename):

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': song_filename
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        return song_filename

    def list_downloaded_songs(self):
        entries = os.scandir("songs/")
        songs = []
        for entry in entries:
            if entry.is_file():
                songs.append(entry.name)

        return songs

    def play(self, voice_channel, song_filename, volume, loop):
        queue = None

        if voice_channel.guild.id in self.queues.keys():
            queue = self.queues[voice_channel.guild.id]

        if not queue or not queue.active:
            queue = MusicQueue(voice_channel, loop)
            self.queues[voice_channel.guild.id] = queue

        source = discord.FFmpegPCMAudio(song_filename)
        source = discord.PCMVolumeTransformer(source)
        source.volume = volume

        queue.queue.put_nowait(source)
