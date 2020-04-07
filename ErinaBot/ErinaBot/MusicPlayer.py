import os
import hashlib
import discord
import youtube_dl

from requests import get
from bs4 import BeautifulSoup


class MusicPlayer():

    def __init__(self):
        pass

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

    def play(self, voice_channel, song_filename, volume):
        if voice_channel.is_playing() or voice_channel.is_paused():
            voice_channel.stop()

        source = discord.FFmpegPCMAudio(song_filename)
        source = discord.PCMVolumeTransformer(source)
        source.volume = volume

        voice_channel.play(source)
        voice_channel.is_playing()
