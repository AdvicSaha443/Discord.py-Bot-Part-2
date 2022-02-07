import discord
import asyncio

from zCommands.zzCommands import Economy, Levels, Auto_Moderation
from discord.ext import commands

msged_people = []

class Spam(commands.Cog):
  def __init__(self, bot):
    self.client = bot
    self.counter = 0
    self.kick = 0

  @commands.Cog.listener()
  async def on_ready(self):
    print('Now Checking For Spams!')
    while True:
      await asyncio.sleep(10)
      self.counter=0
      with open("jsons/msg.txt", "r+") as file:
        file.truncate(0)

  @commands.Cog.listener()
  async def on_message(self, message):
    if not message.author.bot:
      counter = 0
      self.counter+=1
      if self.counter == 10:
        await message.channel.edit(slowmode_delay=15)
        await message.channel.send(f"Enabled Slow Mode In #{message.channel} Of 15 Seconds")
        await asyncio.sleep(60)
        await message.channel.edit(slowmode_delay=0)
      with open("jsons/msg.txt","r+") as file:
        for lines in file:
          if lines.strip("\n") == str(message.author.id):
            counter+=1

        file.writelines(f"{str(message.author.id)}\n")
        if counter >= 5:
          mbed = discord.Embed(
            title = "You Have Been Muted In **Skyblock Server** For 1 Minute",
            description = "Ban Kardunga Pata Bhi Nhi Chalega! ;)",
            color = discord.Color.red()
          )
          mbed2 = discord.Embed(
            title = f"Muted {message.author} For Spamming",
            description = "Ban Kardunga Pata Bhi Nhi Chalega! ;)",
            color = discord.Color.red()
          )
          mbed3 = discord.Embed(
            title = f"Kicked You For Spamming",
            description = "Ban Kardunga Pata Bhi Nhi Chalega! ;)",
            color = discord.Color.red()
          )
          mutedRole = discord.utils.get(message.guild.roles, name="Muted")
          #Economy.decrease_money(str(message.author.id), (counter*100))
          #Levels.decrease_xp(str(message.author.id), str(message.author.guild.id), "xp", (counter*20))
          if self.kick == 0:
            await message.author.add_roles(mutedRole ,reason="Spam")
            await message.channel.send(embed = mbed2)
            await asyncio.sleep(60)
            await message.author.remove_roles(mutedRole)
          else:
            await message.author.ban(reason="Spam")
            await asyncio.sleep(1)
            await message.author.unban()
            await message.author.send(embed=mbed3)

  @commands.command()
  @commands.has_role("Bot-Mod")
  async def k(self, ctx, action= None):
    if action is None: action == "t"
    if action == "t":
      self.kick = 1
    else:
      self.kick = 0
    

def setup(client):
  client.add_cog(Spam(client))

