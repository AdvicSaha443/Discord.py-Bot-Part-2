import discord
import asyncio
import os
import json

from discord.ext import commands, tasks
from zCommands.aternosapi import AternosAPI

headers_cookie = os.environ['headers_cookie']
TOKEN = os.environ['aternos_token']

class Aternos(commands.Cog):
  def __init__(self, bot):
    self.client = bot
    self.server = AternosAPI(headers_cookie, TOKEN, timeout = 10)

  @commands.Cog.listener()
  async def on_ready(self):
    print("Aternos API Ready!")

  @commands.command()
  async def start(self, ctx):
    await ctx.send(self.server.StartServer())

  @commands.command()
  async def status(self, ctx):
    await ctx.send(self.server.GetStatus())

def setup(client):
  client.add_cog(Aternos(client))