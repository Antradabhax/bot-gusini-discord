import discord
import asyncio
import datetime
from discord.ext import commands
from pytube import YouTube
import os

# Define the intents
intents = discord.Intents.default()
intents.typing = True
intents.presences = True
intents.message_content = True

# Create an instance of the bot
bot = commands.Bot(command_prefix='-', intents=intents)

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    # Schedule and send messages here
    await send_scheduled_message()

# Function to create a temporary file with the starting timestamp
def create_temp_file(timestamp):
    with open('temp.txt', 'w') as file:
        file.write(str(timestamp))

# Function to retrieve the elapsed time from the temporary file
def retrieve_elapsed_time():
    if os.path.isfile('temp.txt'):
        with open('temp.txt', 'r') as file:
            return float(file.read())
    return 0.0

# Function to delete the temporary file
def delete_temp_file():
    if os.path.isfile('temp.txt'):
        os.remove('temp.txt')

# Function to send a message to a specific channel
async def send_message(channel_id, message):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message)

# Function to schedule and send a message at a specific time
async def send_scheduled_message():
    target_time = datetime.datetime(2023, 5, 19, 19, 34, 0)  # Specific time in GMT-3
    current_time = datetime.datetime.utcnow() - datetime.timedelta(hours=3)  # Current time in GMT-3
    time_difference = (target_time - current_time).total_seconds()

    # Wait until the scheduled time
    await asyncio.sleep(time_difference)

    # Send the message
    channel_id = 399640256997097474  # Replace with the actual channel ID you want to send the message to
    message = 'nah soy gusini' #<@276044410997702656>
    await send_message(channel_id, message)

@bot.event
async def on_message(message):
    await bot.process_commands(message)

# Command to stop the bot
@bot.command()
async def close(ctx):
    print('Logging out...')
    await bot.close()

# Ping! Pong!
@bot.command()
async def ping(ctx):
    message = 'Pong!'
    channel_id = 399640256997097474
    await send_message(channel_id, message)

@bot.command()
async def g(ctx):
    message = '<@276044410997702656> DA LA CARA!!!'
    channel_id = 399640256997097474
    await ctx.message.delete()
    await send_message(channel_id, message)

@bot.command()
async def status(ctx, member: discord.Member):
    user_status = member.status
    await ctx.message.delete()
    await ctx.send(f"{member.display_name} está {user_status}.")

@bot.command()
async def h(ctx, member: discord.Member):
    is_streaming = member.voice and member.voice.channel.type == discord.ChannelType.voice
    
    user_activities = member.activities
    activities_list = [activity.name for activity in user_activities]

    await ctx.message.delete()
    
    if activities_list:
        activities_str = ', '.join(activities_list)
        if (activities_str == "Hearthstone"):
            await ctx.send(f"Te re fiche jugando Hearthstone <@276044410997702656>!! HDPPPPPPPPPP")
            if(is_streaming):
                await ctx.send(f"Encima el garca no esta stremeandolo ¡¡ALGUIEN HAGA ALGO YA MISMO!!")
    else:
        await ctx.send(f"{member.display_name} no esta haciendo nada. \nSospechoso...")

ffmpeg_path = r'C:\ffmpeg-2023-05-18-git-01d9a84ef5-full_build\bin'

song_timestamps = {}

bot.song_queue = []

ffmpeg_options = {
    'options': '-vn',  # Disable video
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'  # Set additional FFmpeg options
}

@bot.command()
async def play(ctx, url: str):
    voice_channel = ctx.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        voice_client = await voice_channel.connect()

    try:
        video = YouTube(url)
        audio_stream = video.streams.filter(only_audio=True).first()
        audio_url = audio_stream.url

        await ctx.message.delete()

        # Check if there is a song playing
        if voice_client.is_playing() or voice_client.is_paused():
            # Add the audio URL to the song queue
            bot.song_queue.append((audio_url, ctx.author.id))
            await ctx.send("Agregada a la cola!")
        else:
            # Retrieve the elapsed time from the song_timestamps dictionary
            elapsed_time = song_timestamps.get(audio_url, 0.0)

            # Play the song immediately with the provided FFmpeg options
            voice_client.play(
                discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
                after=lambda e: asyncio.run_coroutine_threadsafe(skip(ctx), bot.loop)
            )
            bot.current_song = (url, audio_url)  # Store the current song

            # Store the starting timestamp in the song_timestamps dictionary
            song_timestamps[audio_url] = datetime.datetime.utcnow().timestamp()

            await ctx.send(f"Ahora suena: {url}")

    except Exception as e:
        print(f"Failed to extract audio URL: {str(e)}")
        await ctx.send("Cagamos :(")

@bot.command()
async def skip(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
        voice_client.stop()
        if bot.song_queue:
            # If there are songs in the queue, play the next one
            next_song_url = bot.song_queue.pop(0)
            voice_client.play(discord.FFmpegPCMAudio(next_song_url), after=lambda e: asyncio.run_coroutine_threadsafe(skip(ctx), bot.loop))

            # Store the new starting timestamp in the song_timestamps dictionary
            song_timestamps[next_song_url] = datetime.datetime.utcnow().timestamp()

            await ctx.send("Skipeada")
        else:
            await ctx.send("No hay canciones en la cola!")

@bot.command()
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected():
        voice_client.stop()
        await voice_client.disconnect()
        bot.song_queue.clear()  # Clear the song queue

        # Delete the temporary file
        delete_temp_file()

@bot.command()
async def resume(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("¡Reproducción reanudada!")

@bot.command()
async def pause(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("¡Reproducción pausada!")

@bot.command()
async def ahora(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        current_song = bot.current_song[0]
        await ctx.send(f"Actualmente sonando: {current_song}")
    else:
        await ctx.send("No hay ninguna canción reproduciéndose en este momento.")

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user:  # Ignore voice state changes of the bot itself
        return

    voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
    if voice_client and voice_client.channel and voice_client.channel == before.channel:
        # The bot was disconnected from the voice channel

        # Check if there is a song in progress
        if voice_client.is_playing() or voice_client.is_paused():
            # Retrieve the URL of the current song
            _, audio_url = bot.current_song

            # Retrieve the elapsed time from the song_timestamps dictionary
            elapsed_time = song_timestamps.get(audio_url, 0.0)

            # Remove the current song from the song queue
            bot.song_queue.pop(0)

            # Play the song again from the last known timestamp
            voice_client.play(
                discord.FFmpegPCMAudio(audio_url, options=f"-ss {elapsed_time}"),
                after=lambda e: asyncio.run_coroutine_threadsafe(skip(None, voice_client), bot.loop)
            )

            await asyncio.sleep(1)  # Wait a bit to ensure playback starts

@bot.command()
async def ayuda(ctx):
    message = 'Negrata... \n-play\n-stop\n-skip\n-resume\n-pause\n-ahora\n-status (etiqueta a alguien)\n-h (gusini jugando)\n-g (para que den la cara)\n-ping'
    await ctx.send(message)

# Run the bot
bot.run('MTAxOTY3NTIxOTc4NDM2ODE4OA.GaFyIp.nCB4dJSXtaEmE4kwZseTbMPm499wOnt6E8VNPo')  # Replace with your actual bot token obtained from the Discord Developer Portal
