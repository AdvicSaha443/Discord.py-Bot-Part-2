import discord
import asyncio
import datetime
import json

from discord.ext import commands, tasks
from zCommands.zzCommands import Time

class Birthday(commands.Cog):
  def __init__(self, bot):
    self.client = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print('Birthday Cog Ready!')

  @commands.command()
  async def set_birthday(self ,ctx, day: int, month: int, year: int):
    try:
      if month > 13 or month < 1:
              await ctx.send("Please Enter A Valid Date!")
              return
      else:
        pass    
      if month in (1, 3, 5, 7, 8, 10, 12):
          if day > 31 or day < 1:
              await ctx.send("Please Enter A Valid Date!")
              return
          else:
              pass
      elif month in (4, 6, 9, 11):
          if day > 30 or day < 1:
              await ctx.send("Please Enter A Valid Date!")
              return
          else:
              pass
      elif month == 2:
          if day > 29 or day < 1:
              await ctx.send("Please Enter A Valid Date!")
              return
          else:
              pass
      else:
          await ctx.send("Please Enter A Valid Date!")
          return
    except:
        await ctx.send("Please Enter A Valid Date!")
        return
    
    with open("jsons/birthday.json", "r") as f:
      users = json.load(f)

    users[str(ctx.author.id)] = {}
    users[str(ctx.author.id)]['day'] = day
    users[str(ctx.author.id)]['month'] = month
    users[str(ctx.author.id)]['year'] = year
    users[str(ctx.author.id)]['wished'] = 0

    with open("jsons/birthday.json", "w") as f:
      json.dump(users, f)
    
    m = Time.month(month)
    e = Time.day(day)

    await ctx.send(f"Duly Noted! I'll Wish {ctx.author.mention} on **{day}{e}-{m}!**")

def setup(client):
  client.add_cog(Birthday(client))

