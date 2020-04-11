import os
import re
import hashlib
import discord
import youtube_dl
import asyncio
import itertools
import unidecode

from async_timeout import timeout
from requests import get
from bs4 import BeautifulSoup


class MusicQueue():

    def __init__(self, text_channel, channel, loop):
        self.queue = asyncio.Queue(maxsize=10)
        self.next = asyncio.Event()

        self.text_channel = text_channel
        self.channel = channel
        self.loop = loop

        self.task = self.loop.create_task(self.queue_worker())
        self.active = True
        self.volume = 1

    async def destroy(self):
        await self.channel.disconnect()
        self.active = False
        self.task.cancel()

    async def queue_worker(self):
        while self.active:
            self.next.clear()

            try:
                async with timeout(180):
                    element = await self.queue.get()

            except asyncio.TimeoutError:
                await self.text_channel.send("Nadie esta escuchando musica, salgo del canal de voz :pleading_face:")
                await self.destroy()
                continue

            if not self.channel.is_connected():
                await self.destroy()
                continue

            embed = (discord.Embed(title=":headphones: Ahora suena", description=element["name"], color=discord.Color.purple())
                    .set_thumbnail(url=element['thumbnail'])
                    .add_field(name="Requested By", value=element['requested_by'])
                    .add_field(name="Enlaces", value="[YouTube](%s)" %(element['url'])))

            await self.text_channel.send(embed=embed)

            source = element["source"]

            source.volume = self.volume

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

    def get_queue(self, text_channel, voice_channel, loop):
        queue = None

        if voice_channel.guild.id in self.queues.keys():
            queue = self.queues[voice_channel.guild.id]

        if not queue or not queue.active:
            queue = MusicQueue(text_channel, voice_channel, loop)
            self.queues[voice_channel.guild.id] = queue

        return queue

    def remove_queue(self, voice_channel):
        if voice_channel.guild.id in self.queues.keys():
            del self.queues[voice_channel.guild.id]

    def set_volume(self, voice_channel, volume):
        if voice_channel.guild.id in self.queues.keys():
            queue = self.queues[voice_channel.guild.id]

        else:
            return

        queue.volume = volume
        voice_channel.source.volume = volume

    def get_queue_info(self, voice_channel):
        if voice_channel.guild.id in self.queues.keys():
            queue = self.queues[voice_channel.guild.id]

        else:
            return None

        if queue.queue.empty():
            return None

        upcoming = list(itertools.islice(queue.queue._queue, 0, 5))
        return upcoming

    def search_yt_video(self, query):
        response = get("https://www.youtube.com/results?search_query=%s" %(query))

        soup = BeautifulSoup(response.text, 'lxml')

        videos = []
        for vid in soup.find_all(attrs={'class':'yt-uix-tile-link'}, limit=10):
            url = 'https://www.youtube.com' + vid['href']
            name = vid['title']

            if not "user" in url and not "channel" in url and not "playlist" in url:
                videos.append({'url':url, 'name':name})

        return videos

    def download_yt_video(self, url):
        if "user" in url or "channel" in url or "playlist" in url:
            return False, False, False

        response = get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        song_filename = soup.find("meta", attrs={'property':'og:title'})['content']
        song_thumbnail = soup.find("meta", attrs={'property':'og:image'})['content']

        song_path = "songs/%s.mp3" %(song_filename)

        if not os.path.exists(song_path):
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'songs/' + song_filename + '.%(ext)s'
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        if not os.path.exists(song_path):
            return False, False, False

        return song_path, song_filename, song_thumbnail

    def list_downloaded_songs(self):
        entries = os.scandir("songs/")
        songs = []
        for entry in entries:
            if entry.is_file():
                songs.append(entry.name)

        return songs

    def play(self, text_channel, voice_channel, path, loop, metadata):
        queue = self.get_queue(text_channel, voice_channel, loop)

        source = discord.FFmpegPCMAudio(path)
        source = discord.PCMVolumeTransformer(source)

        song = {
            "source": source,
            "name": metadata['name'],
            "thumbnail": metadata['thumbnail'],
            "url": metadata['url'],
            "requested_by": metadata['requested_by']
        }

        queue.queue.put_nowait(song)
