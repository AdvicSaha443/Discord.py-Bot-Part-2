import discord
import os
import json
import asyncio

from discord import Member, File
from discord.ext import commands
from datetime import datetime
from pymongo import MongoClient
from typing import Optional
from zCommands.zzCommands import Levels, General, Economy

level = ['Level-5+', 'Level-10+', 'Level-15+', 'Level-20+', 'Level-25+', 'Level-30+', 'Level-40+', 'Level-50+', 'Level-75+', 'Level-100+', 'Level-150+']
levelnum = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150]

my_secret = os.environ['clusterr']
cluster = MongoClient(my_secret)

levelling = cluster["DiscordBot"]["Levelling"]

numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
		   "6⃣", "7⃣", "8⃣", "9⃣", "🔟")

class Levelsys(commands.Cog):

  def __init__(self, bot):
    self.client = bot
    self.polls = []

  @commands.Cog.listener()
  async def on_ready(self):
    print('Levelling System Now Online!')

  @commands.command()
  async def rank(self, ctx, user: Optional[discord.Member]):
    if ctx.guild is not None:
      Levels.add_user_all_guild_data(ctx.author)
      userr = user or ctx.author
      file = await Levels.make_user_rank_card(str(ctx.author.guild.id), userr.id, userr.avatar_url, str(userr))
      if file == 0:
        await ctx.send(f"{user.name} Don't Have Any Xp")
        return
      await ctx.send(file=file)
    else:
      await ctx.send("Rank Command Isn't Available In Bot DM")

  @commands.command()
  async def rank_info(self, ctx, user: Optional[discord.Member]):
    if ctx.guild is not None:
      userr = user or ctx.author
      Levels.add_user_all_guild_data(ctx.author)
      data = Levels.get_rank_info(userr.id)
      
      mbed=discord.Embed(
        title=f"{userr.name}'s Rank Info",
        color=discord.Color.from_rgb(255, 255, 255)
      )

      if data == "newuser":
        await ctx.send(f"No data found for {userr.mention}")
        return

      mbed.add_field(name="Current Xp", value=data.get("xp"), inline=False)
      mbed.add_field(name="Current Level", value=data.get("level"), inline=False)
      mbed.add_field(name="Next Level Xp", value=data.get("xp_for_next_level"), inline=False)
      mbed.add_field(name="Xp More Needed", value=data.get("xp_need"), inline=False)
      mbed.add_field(name="Percentage Done", value=data.get("percent_done"), inline=False)
      mbed.add_field(name="Message More Need to Send", value=data.get("message_more_needed"), inline=False)

      mbed.set_thumbnail(url=userr.avatar_url)
      mbed.set_footer(text=f"{userr}'s Rank Info'", icon_url=userr.avatar_url)

      await ctx.send(embed=mbed)
    else:
      await ctx.send("Rank Info Command Isn't Available In Bot DM")

  @commands.command()
  async def backgrounds(self, ctx):
    if ctx.guild is None:
      for i in range(0, 4):
        file = File(filename=f"images/{i}.png")
        await ctx.send(file=file)

  @commands.command()
  async def change_background(ctx):
    pass

  @commands.command(name="leaderboard")
  async def leaderboard(self, ctx, range_num=5):
    with open("jsons/levels.json", "r") as f:
      data = json.load(f)

    l = {}
    total_xp = []

    for userid in data:
      xp = int(data[str(userid)]['xp']+(int(data[str(userid)]['level'])*100))

      l[xp] = f"{userid};{data[str(userid)]['level']};{data[str(userid)]['xp']}"
      total_xp.append(xp)

    total_xp = sorted(total_xp, reverse=True)
    index=1

    mbed = discord.Embed(
      title="Leaderboard Command Results"
    )

    for amt in total_xp:
      id_ = int(str(l[amt]).split(";")[0])
      level = int(str(l[amt]).split(";")[1])
      xp = int(str(l[amt]).split(";")[2])

      member = await self.bot.fetch_user(id_)

      if member is not None:
        name = member.name
        mbed.add_field(name=f"{index}. {name}",
        value=f"**Level: {level} | XP: {xp}**", 
        inline=False)

        if index == range_num:
          break
        else:
          index += 1

    await ctx.send(embed = mbed)


  @commands.command()
  @commands.has_role("Server-Mod")
  async def increase_xp(self, ctx, userid: str, increaseby: int):
    Levels.increase_xp(userid, ctx.author.id, increaseby)
    await ctx.send(f"Increased Xp by {increaseby}; if your level is increased then this won't tell")

  @commands.command()
  @commands.has_role("Server-Mod")
  async def decrease_xp(self, ctx, userid: str, decreaseby: int):
    Levels.decrease_xp(userid, ctx.author.id, decreaseby)
    await ctx.send(f"Decreased Xp by {decreaseby}; if your level is decreased then this won't tell")
  
  @commands.command(name="mkpoll")
  async def create_poll(self, ctx, hours: int, question: str, *options):
    with open("jsons/mainBank.json", "r") as f:
      data = json.load(f)

    if not data[str(ctx.author.id)]['bank'] >= 10000:
      await ctx.send("You don't Have enough Coin to conduct a poll! \n *you need 10000 coins(in your wallet) to conduct a poll*")
    else:
      Economy.update_bank_using_id(ctx.author.id, -1*10000, "wallet")
      Economy.update_bank_using_id(ctx.guild.id, 10000, "bank")
      if len(options) > 10:
        await ctx.send("You Can Only Supply a Maximum Of 10 Options!")
      else:
        mbed = discord.Embed(
          title=f"{question}",
          description=f"Poll By {ctx.author}",
          color = ctx.author.colour,
          timestamp=datetime.utcnow()
        )
        fields = [("Options: ", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
              ("Instructions: ", "React to cast a vote!", False)]

        dict = {}
        count = 0

        emojis_dict = {
          "1️⃣": "1",
          "2⃣": "2",
          "3⃣": "3",
          "4⃣": "4",
          "5⃣": "5",
          "6⃣": "6",
          "7⃣": "7",
          "8⃣": "8",
          "9⃣": "9",
          "🔟": "10"
        }

        for option in options:
          count = count+1
          dict[count] = option
        
        for name, value, inline in fields:
          mbed.add_field(name=name, value=value, inline=inline)
        
        message = await ctx.send(embed=mbed)
        await ctx.message.delete()

        for emoji in numbers[:len(options)]:
          await message.add_reaction(emoji)

        self.polls.append((message.channel.id, message.id))

        await asyncio.sleep(hours)

        print(message.reactions)

        cache_msg = discord.utils.get(self.client.cached_messages, id=message.id)
        
        most_voted = max(cache_msg.reactions, key=lambda r: r.count)
        await cache_msg.delete()

        mbed2 = discord.Embed(
          title=f"Poll Has Ended",
          description=f"**Question: {question}**",
          color=ctx.author.colour
        )

        print(dict.get(str(emojis_dict.get(str(most_voted.emoji)))))

        mbed2.add_field(name="Options: ", value="\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), inline=False)
        mbed2.add_field(name=f"Most Voted With {most_voted.count-1:}: ", value=f"{most_voted.emoji}: {dict.get(int(emojis_dict.get(str(most_voted.emoji))))}")

        await ctx.send(embed=mbed2)

  async def send_embed_main(self, title:str, message:str, color:str, channel_id:str):
    try:
      mbed = discord.Embed(
        title=title,
        description=message,
        color=color,
      )
    except Exception as e:
      return f"{e} + + exit_code 0"
    try:
      channel = self.client.get_channel(channel_id)
      await channel.send(embed=mbed)
    except Exception as e:
      return f"{e} + + exit_code 1"
    return "message_sent + + exit_code 2" 


def setup(client):
  client.add_cog(Levelsys(client))

