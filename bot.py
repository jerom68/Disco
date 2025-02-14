import discord
import requests
import aiohttp
import os
import asyncio
import psutil
from discord.ext import commands, tasks

# Bot settings
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Time in seconds before sleeping (30 min = 1800 sec)
INACTIVITY_LIMIT = 1200  # 30 minutes of inactivity

# Last active timestamp
last_active = None

# Railway Webhook URL (Replace with your webhook URL)
RAILWAY_DEPLOY_HOOK = os.getenv("RAILWAY_HOOK_URL")

# Fun command: Send a random anime quote
@bot.command()
async def animequote(ctx):
    global last_active
    last_active = asyncio.get_event_loop().time()
    url = "https://animechan.xyz/api/random"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                await ctx.send(f'"{data["quote"]}" - {data["character"]} ({data["anime"]})')
            else:
                await ctx.send("Couldn't fetch an anime quote. Try again later.")

# Fun command: Get Pokémon info
@bot.command()
async def pokemon(ctx, name: str):
    global last_active
    last_active = asyncio.get_event_loop().time()
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        abilities = ", ".join([a["ability"]["name"] for a in data["abilities"]])
        await ctx.send(f"**{data['name'].title()}**\nAbilities: {abilities}\nWeight: {data['weight']}")
    else:
        await ctx.send("Pokémon not found!")

# Fun command: Generate a random meme (Imgflip API)
@bot.command()
async def meme(ctx):
    global last_active
    last_active = asyncio.get_event_loop().time()
    url = "https://api.imgflip.com/get_memes"
    response = requests.get(url)
    if response.status_code == 200:
        memes = response.json()['data']['memes']
        meme = memes[0]  # Select the first meme
        await ctx.send(meme['url'])
    else:
        await ctx.send("Couldn't fetch a meme. Try again later.")

# Fun command: Get character info by name (Anime Character API)
@bot.command()
async def character(ctx, name: str):
    global last_active
    last_active = asyncio.get_event_loop().time()
    url = f"https://api.jikan.moe/v3/search/character?q={name}&limit=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()['results'][0]
        await ctx.send(f"**{data['name']}**\nAnime: {data['anime'][0]['name']}\nImage: {data['image_url']}")
    else:
        await ctx.send("Character not found!")

# Fun command: AI Image generation (Replace with DALL·E API or similar service)
@bot.command()
async def imagine(ctx, *, prompt: str):
    global last_active
    last_active = asyncio.get_event_loop().time()
    await ctx.send(f"Imagine command received: {prompt}\n(This would generate an image using AI, but needs an API integration.)")

# Fun command: Auto Slowmode (Set a slowmode automatically when bot detects spamming)
@bot.command()
async def setslowmode(ctx, time: int):
    """Sets slowmode automatically when there is spam in chat."""
    await ctx.channel.edit(slowmode_delay=time)
    await ctx.send(f"Slowmode set to {time} seconds.")

# Auto-sleep function
async def auto_sleep():
    global last_active
    while True:
        await asyncio.sleep(60)  # Check every minute
        if last_active and (asyncio.get_event_loop().time() - last_active) > INACTIVITY_LIMIT:
            print("Bot is inactive. Shutting down to save Railway hours.")
            await bot.close()  # Stop the bot

# Command to restart the bot using Railway Webhook
@bot.command()
async def wake(ctx):
    if RAILWAY_DEPLOY_HOOK:
        async with aiohttp.ClientSession() as session:
            async with session.post(RAILWAY_DEPLOY_HOOK) as response:
                if response.status == 200:
                    await ctx.send("Bot is restarting...")
                else:
                    await ctx.send("Failed to restart bot.")
    else:
        await ctx.send("No restart URL configured.")

# Event: Bot is ready
@bot.event
async def on_ready():
    global last_active
    last_active = asyncio.get_event_loop().time()
    print(f"Logged in as {bot.user}")

# Run auto-sleep in background
bot.loop.create_task(auto_sleep())

# Start the bot
bot.run(os.getenv("BOT_TOKEN"))
