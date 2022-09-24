import discord
from discord.ext import commands
from discord.ext import tasks
from os import getenv
import traceback
import datetime
import scraping

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Botのアクセストークン
TOKEN = 'TOKEN'
# 投稿するチャンネルID
CHANNEL_ID = 1020404427766644756


@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(
        traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@tasks.loop(hours=1)
async def loop():
    # botが起動するまで待つ
    await bot.wait_until_ready()
    if not scraping.task():
        return
    channel = bot.get_channel(CHANNEL_ID)
    # 更新監視
    embeds = scraping.scraping_FL()
    await channel.send(datetime.datetime.now().isoformat(), embeds=embeds)


token = getenv('DISCORD_BOT_TOKEN')
bot.run(token)
# bot.run(TOKEN)
