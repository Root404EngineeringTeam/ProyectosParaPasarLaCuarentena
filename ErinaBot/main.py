from __future__ import unicode_literals
import ErinaBot
import discord
import time
import os
import re

client = discord.Client()

@client.event
async def on_ready():
    print("The bot is ready!")
    activity = discord.Game(name="Making a bot")
    await client.change_presence(status=discord.Status.online, activity=activity)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if (not client.user in message.mentions) and (not message.mention_everyone):
        return

    context = ErinaBot.conversation.get_context(message.channel)
    answer = ErinaBot.conversation.recognize(message.content)

    regex = re.search(r'\"(.+)\"', message.content)
    if (answer == "yt_search" and not context) or (regex and context == "yt_search"):
        ErinaBot.conversation.set_context(message.channel, 'yt_search')

        if not regex:
            await message.channel.send("Que busco?")
            return

        query = regex.group(1)
        await message.channel.send("Buscando **%s** :face_with_monocle:" %(query))

        videos = ErinaBot.music.search_yt_video(query)

        string = "```"

        for i in range(len(videos)):
            video = videos[i]
            string += "%s: %s\n" %(i, video['name'])

        await message.channel.send(string + "```")

        ErinaBot.conversation.set_context_var(message.channel, "yt_search_result", videos)
        ErinaBot.conversation.set_context(message.channel, 'play_music')
        return

    regex1 = re.search(r'\"(.+)\"', message.content)
    regex2 = re.search(
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})', message.content)
    regex3 = re.search(r'(el|la)\s+([0-9])', message.content)

    if (answer == "play_music" and not context) or ((regex1 or regex2) and context == "play_music") or regex3:
        ErinaBot.conversation.set_context(message.channel, 'play_music')

        voice_channel = await ErinaBot.music.get_voice_channel(client, message.author)

        if not voice_channel:
            await message.channel.send("Conectate a un canal de voz y ahi la pongo :rolling_eyes:")
            ErinaBot.conversation.clear_context(message.channel)
            return

        if regex2:
            url = "http://www.youtube.com/watch?v=%s" %(regex2.group(6))
            await message.channel.send("Dame un segundo...")

        elif regex1:
            if "tusa" in message.content:
                await message.channel.send("Weyyy nooooo! la cancion! :sob::ok_hand::ok_hand::ok_hand:")
            else:
                await message.channel.send("%s:notes::notes:" %(regex1.group(1)))

            url = ErinaBot.music.search_yt_video(regex1.group(1))[0]['url']

        elif regex3:
            index = int(regex3.group(2))
            videos = ErinaBot.conversation.get_context_var(message.channel, "yt_search_result")

            if not videos:
                await message.channel.send("Debo buscar canciones primero :thinking:")
                return

            url = videos[index]['url']
            await message.channel.send("A la orden mi cap! :sunglasses:")

        else:
            await message.channel.send("Que cancion quieres?")
            return

        if not url:
            ErinaBot.conversation.clear_context(message.channel)
            await message.channel.send("Los siento no pude encontrarla :C intenta de nuevo")
            return

        song_filename = ErinaBot.music.download_yt_video(url)
        volume = ErinaBot.conversation.get_context_var(message.channel, "player_volume")

        if not volume:
            volume = 1

        ErinaBot.music.play(voice_channel, song_filename, volume)

        ErinaBot.conversation.clear_context(message.channel)
        return

    regex = re.search(r'(en|de)\s+(\w+)', message.content)

    if (answer == "covid" and not context) or (regex and context == "covid"):
        ErinaBot.conversation.set_context(message.channel, 'covid')

        if regex:
            country = regex.group(2)

        else:
            await message.channel.send("De que pais?")
            return

        ErinaBot.conversation.clear_context(message.channel)

        await message.channel.send("Voy, dame un segundo...")
        await message.channel.send(ErinaBot.utils.covid_cases(country))
        return

    regex = re.search(r'(de)\s+(\w+)', message.content)
    if (answer == "send_nudes" and not context) or (("tuyo" in message.content or regex) and context == "send_nudes"):
        ErinaBot.conversation.set_context(message.channel, 'send_nudes')

        if regex:
            topic = regex.group(2)
        elif "tuyo" in message.content:
            topic = "nier"
        else:
            await message.channel.send("Pinshi puerco... de quien quieres nudes? 7u7r")
            return

        ErinaBot.conversation.clear_context(message.channel)

        await message.channel.send("Ah prrooooo... voy espera 7u7r")
        await message.channel.send(ErinaBot.utils.get_nudes(topic))
        await message.channel.send(":smiling_imp:")
        return

    regex1 = re.search(r'\"(.+)\"', message.content)
    regex2 = re.search(r'(en)\s+([0-9]+)\s+(minuto|hora|dia)', message.content)
    if (answer == "reminder" and not context) or ((regex1 or regex2) and context == "reminder"):
        ErinaBot.conversation.set_context(message.channel, 'reminder')

        value = ErinaBot.conversation.get_context_var(message.channel, 'notification_value')
        when = ErinaBot.conversation.get_context_var(message.channel, 'notification_when')

        if not regex1 and not value:
            await message.channel.send("Que quieres que te recuerde?")
            return

        if regex1 and not value:
            value = regex1.group(1)
            ErinaBot.conversation.set_context_var(message.channel, 'notification_value', value)

        if not regex2 and not when:
            await message.channel.send("Para cuando?")
            return

        if regex2 and not when:
            when = "%s %s" %(regex2.group(2), regex2.group(3))
            ErinaBot.conversation.set_context_var(message.channel, 'notification_when', when)

        ErinaBot.conversation.set_context_var(message.channel, 'notification_value', '')
        ErinaBot.conversation.set_context_var(message.channel, 'notification_when', '')

        expiration, type = when.split(" ")
        expiration = int(expiration)

        if "minuto" in type:
            expiration = expiration * 60

        elif "hora" in type:
            expiration = expiration * 60 * 60

        elif "dia" in type:
            expiration = expiration * 24 * 60 * 60

        notification = {
            'expiration': time.time() + expiration,
            'message': value,
            'author': message.author.name
        }

        ErinaBot.db.notifications.insert_one(notification)

        ErinaBot.conversation.clear_context(message.channel)

        await message.channel.send("Vale yo te aviso :sunglasses:")
        return

    if answer == "meme" and not context:
        await message.channel.send("Deja busco uno que este bueno :'3 ...")
        await message.channel.send(ErinaBot.utils.get_meme())
        return

    if answer == "joke" and not context:
        await message.channel.send("Mmm ...")
        await message.channel.send(ErinaBot.utils.get_joke())
        return

    if (answer == "pause_music" and not context):
        voice_channel = await ErinaBot.music.get_voice_channel(client, message.author)

        if not voice_channel:
            await message.channel.send("No estoy conectada a ningun canal de voz :rolling_eyes:")
            return

        if voice_channel.is_playing():
            await message.channel.send("Musica en pausa  :'c :mute:")
            voice_channel.pause()

        else:
            await message.channel.send("No se esta reproduciendo nada :thinking:")

        return

    if (answer == "leave_voice_channel" and not context):
        voice_channel = await ErinaBot.music.get_voice_channel(client, message.author)

        if not voice_channel:
            await message.channel.send("No estoy conectada a ningun canal de voz :rolling_eyes:")
            return

        await message.channel.send("Ay :c al fin que ni queria hablar con ustedes :'v :broken_heart:")
        await voice_channel.disconnect()
        return

    if (answer == "resume_music" and not context):
        voice_channel = await ErinaBot.music.get_voice_channel(client, message.author)

        if not voice_channel:
            await message.channel.send("No estoy conectada a ningun canal de voz :rolling_eyes:")
            return

        if voice_channel.is_paused():
            await message.channel.send("Fierro :cowboy: :ok_hand:")
            voice_channel.resume()

        else:
            await message.channel.send("No se esta reproduciendo nada :thinking:")

        return

    regex = re.search(r'([0-9]+)', message.content)
    if (answer == "volume" and not context):
        voice_channel = await ErinaBot.music.get_voice_channel(client, message.author)

        if not voice_channel:
            await message.channel.send("No estoy conectada a ningun canal de voz :rolling_eyes:")
            return

        if "baja" in message.content:
            volume = voice_channel.source.volume - 0.1

        elif regex:
            volume = int(regex.group(1)) / 100

        else:
            volume = voice_channel.source.volume + 0.1

        if volume < 0:
            volume = 0
        elif volume > 1:
            volume = 1

        voice_channel.source.volume = volume
        ErinaBot.conversation.set_context_var(message.channel, "player_volume", volume)
        await message.channel.send("Volumen: **%i** :loud_sound:" %(volume * 100))
        return


    if answer == "clear_context":
        ErinaBot.conversation.clear_context(message.channel)
        await message.channel.send("Mmm bueno...")
        return

    ErinaBot.conversation.clear_context(message.channel)
    await message.channel.send(answer)

client.run(ErinaBot.access_token)
