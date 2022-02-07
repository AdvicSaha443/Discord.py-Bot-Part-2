import discord
import asyncio
import json

from discord.ext import commands
from better_profanity import profanity
from zCommands.zzCommands import Economy, Levels

class Check(commands.Cog):
  def __init__(self, bot):
    self.client = bot
    self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

  @commands.Cog.listener()
  async def on_ready(self):
    print('Now Checking Messages!')

  profanity.load_censor_words_from_file('jsons/badwords.txt')

  @commands.Cog.listener()
  async def on_message(self, message):
    if not message.author.bot:
      if profanity.contains_profanity(message.content):
        mbed = discord.Embed(
          title = str(message.author) + ' ' + 'Has Been Warned For Using A Bad Word',
          description = "Ban Kardunga Pata Bhi Nhi Chalega! ;)",
          color = discord.Color.red()
        )
        Economy.decrease_user_money(int(5000), str(message.author.id), str(message.guild.id))
        await message.delete()
        await message.channel.send(embed = mbed)
        await message.author.send("You Can't Use That Word Here!")
        return
      else:
        if message.guild is not None:
          if not message.content.startswith('?'):
            Economy.increase_money(str(message.author.id), str(message.guild.id))
            recieved_data = Levels.increase_xp(str(message.author.id), str(message.guild.id), int(20))
            if recieved_data == "NONE":
              return
            else:
              data = recieved_data.split(" ")
              if data[0] == "NEW-LEVEL":
                await message.channel.send(f"{message.author.mention} Just Leveled Up To **Level: {data[1]}**!")
              elif data[0] == "NEW-LEVEL-ROLES":
                await message.author.add_roles(discord.utils.get(message.author.guild.roles, name=data[2]))
                mbed = discord.Embed(title=f"{message.author} You Have Gotten role **{data[2]}**!", color = message.author.colour)
                mbed.set_thumbnail(url=message.author.avatar_url)
                await message.channel.send(embed=mbed)
              else:
                print("LOL ERROR")
          else: 
            return
        else:
          return

def setup(client):
  client.add_cog(Check(client))

