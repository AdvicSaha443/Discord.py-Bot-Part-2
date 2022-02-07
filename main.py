import discord
import os
import asyncio
import json
import random
import subprocess
import aiohttp
import requests

from discord import File
from flask import jsonify
from discord.utils import get
from discord.ext import commands
from datetime import datetime
from dashboard.keep_alive import keep_alive
from pymongo import MongoClient
from typing import Optional
from zCommands.zzCommands import Economy, Time, General
from easy_pil import Editor, Font, Text, load_image_async

intents = discord.Intents.default()
intents.members = True
token = os.environ['token']

bot = commands.Bot(command_prefix='?', intents=intents)
bot.remove_command('help')

client = discord.Client(intents=intents)

my_secret = os.environ['clusterr']
cluster = MongoClient(my_secret)

adv_db = cluster["DiscordBot"]["Adventure"]

adv_people = []
giveaway = False
server_in_lockdown = ["no_lockdown"]


@bot.event
async def on_ready():
    channel = bot.get_channel(905720504084750376)
    await channel.send(f"Bot Restarted At {datetime.now()} With {round(bot.latency * 1000)} ms Latency")
    print('Bot Now Online')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing, name="Bot Just Woke Up!"))
    await asyncio.sleep(10)
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="?help | Visit a.advic.repl.co"))


@bot.command()
@commands.has_role("Bot-Mod")
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f"Loaded {extension} cog")


@bot.command()
@commands.has_role("Bot-Mod")
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f"Unloaded {extension} cog")


@bot.command()
@commands.has_role("Bot-Mod")
async def load_all_cogs(ctx):
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(
                                  type=discord.ActivityType.watching,
                                  name="?sb_help"))


@bot.command()
@commands.has_role("Bot-Mod")
async def unload_all_cogs(ctx):
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
    await bot.change_presence(status=discord.Status.idle)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


@bot.command()
async def checking(ctx):
    await ctx.send(" \:amongus: ")


@bot.command()
async def ping(ctx):
    await ctx.send(f'Bot Latency: {round(bot.latency * 1000)} ms')


@bot.command()
async def announcement_add(ctx, *, announcement=None):
    announcement_user = []
    announcement_role = discord.utils.get(ctx.guild.roles,
                                          name="announcements")
    for member in ctx.guild.members:
        if announcement_role in member.roles:
            announcement_user.append(member.name + '#' + member.discriminator)

    if str(ctx.author) in announcement_user:
        if announcement != None:
            channel = bot.get_channel(873465171132166144)
            allowed_mentions = discord.AllowedMentions(everyone=True)

            mbed = discord.Embed(title='Announcement',
                                 description=announcement,
                                 timestamp=datetime.utcnow(),
                                 color=discord.Color.blue())
            mbed.set_thumbnail(
                url=
                'https://cdn.discordapp.com/attachments/822717749725757460/874539242292916264/latest.png'
            )

            mbed2 = discord.Embed(title='Announcement Added!',
                                  color=discord.Color.from_rgb(255, 255, 255))

            await ctx.message.delete()
            await channel.send(content="@everyone",
                               allowed_mentions=allowed_mentions,
                               embed=mbed)
            await ctx.channel.send(ctx.author.mention, embed=mbed2)
        else:
            await ctx.channel.send(
                f'{ctx.author.mention} No Announcement Given!')
    else:
        msg = ctx.author.mention + ' ' + 'You Dont Have Permission For This'
        await ctx.channel.send(msg)


@bot.command()
async def request_make(ctx, *, request=None):
    if request != None:
        channel = bot.get_channel(873466841912213534)

        mbed = discord.Embed(title='Request Made By ' + ctx.author.name,
                             description=request,
                             timestamp=datetime.utcnow(),
                             color=discord.Color.teal())
        mbed2 = discord.Embed(title='Request Added!',
                              color=discord.Color.from_rgb(255, 255, 255))
        mbed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.message.delete()
        await channel.send(embed=mbed)
        await ctx.channel.send(ctx.author.mention, embed=mbed2)
    else:
        await ctx.channel.send(f'{ctx.author.mention} No Request Given!')


########################################################### HELP COMMANDS


@bot.command()
async def help(ctx):
    mbed = discord.Embed(
        title='**Skyblock Bot Help**',
        description='All Commands',
        color=discord.Color.from_rgb(255, 255, 255),
    )
    fields = [
        ("General Commands", "?general_help", False),
        ('Moderation Commands', '?mod_help', False),
        ("Music Commands", "?music_help", False),
        ("Bank Commands", "?bank_help", False),
    ]

    for name, value, inline in fields:
        mbed.add_field(name=name, value=value, inline=inline)
    mbed.set_thumbnail(
        url=
        'https://cdn.discordapp.com/attachments/822717749725757460/874358230199992360/unknown.png'
    )

    await ctx.channel.send(embed=mbed)

@bot.command(name="general_help")
async def general_help(ctx):
  mbed = discord.Embed(title='**SkyBlock Bot General Help**',
                         description='All Moderation Commands',
                         color=discord.Color.from_rgb(255, 255, 255))
  fields = [("Add Announcement", "?announcement_add [announcement]", True),
  ("Make Request", "?request_make [request]", False),
  ("Set Birthday", "?set_birthday [day] [month] [year]", False)]

  for name, value, inline in fields:
      mbed.add_field(name=name, value=value, inline=inline)
  mbed.set_thumbnail(
      url=
      'https://cdn.discordapp.com/attachments/822717749725757460/874358230199992360/unknown.png'
  )
  mbed.set_footer(text='*You Need To Be A Server Mod To Use These Commands')
  await ctx.channel.send(embed=mbed)

@bot.command()
async def mod_help(ctx):
    mbed = discord.Embed(title='**SkyBlock Bot Moderation Help**',
                         description='All Moderation Commands',
                         color=discord.Color.from_rgb(255, 255, 255))
    fields = [("Mod", "?mod [Member]", True),
              ("Warn User", "?warn_user [Member] [Reason]", False),
              ("Kick User", "?kick [Member] [Optional Reason]", False),
              ("Ban User", "?ban [Member] [Optional Reason]", False),
              ("Unban User", "?unban [Member]", False),
              ("Tempporary Mute", "?temp_mute [Member] [Seconds]", False),
              ("Server Lockdown", "?server_lockdown", False),
              ("Over Server Lockdown", "?over_server_lockdown", False),
              ("Slowmode", "?sm [seconds]", False),
              ("Lock Channel", "?lock [Optional Channel]", False),
              ("Unlock Channel", "?unlock [Optional Channel]", False),
              ("Clear Message", "?clear [Count]", False)]
    for name, value, inline in fields:
        mbed.add_field(name=name, value=value, inline=inline)
    mbed.set_thumbnail(
        url=
        'https://cdn.discordapp.com/attachments/822717749725757460/874358230199992360/unknown.png'
    )
    mbed.set_footer(text='*You Need To Be A Server Mod To Use These Commands')
    await ctx.channel.send(embed=mbed)


@bot.command()
async def music_help(ctx):
    mbed = discord.Embed(title='**SkyBlock Bot Music Help**',
                         description='All Music Commands',
                         color=discord.Color.from_rgb(255, 255, 255))
    fields = [
        ("?join [Channel Id]", "Joins A Voice Channel", True),
        ("?yt [Music Name or Youtube Link]",
         "Plays The Song In The Voice Channel", False),
        ("?pause", "Pauses The Song", False),
        ("?play", "Resumes The Song", False),
        ("?stop", "Stops The Song And Ends The Queue", False),
        ("?queue", "Displayes Queue", False),
        ("?previous", "Plays The Previous Song In The Queue", False),
        ("?skip", "Plays The Next Song In The Queue", False),
        ("?playing", "Displayes The Song Currently Playing", False),
        ("?restart", "Restarts The Currently Playing Song", False),
        ("?shuffle", "Shuffle The Queue", False),
        ("?stop", "Stops The Song And Ends The Queue", False),
        ("?volume [Volume *in Int]", "Changes The Volume Of The Song", False),
        ("?disconnect", "Stops The Music And Dissconnects From The Voice Channel", False),
        ("?save_playlist [Playlist URL] [Playlist Name]", "Save Your Playlist!", False),
        ("?change_playlist [New Playlist URL] [New Playlist Name]", "Change Your Playlist!", False),
        ("?get_playlist [Optional User]", "Get Your Or Other users's playlist!", False),
    ]
    for name, value, inline in fields:
        mbed.add_field(name=name, value=value, inline=inline)
    mbed.set_thumbnail(
        url=
        'https://cdn.discordapp.com/attachments/822717749725757460/874358230199992360/unknown.png'
    )
    mbed.set_footer(text='*Use These Commands In #Music Channel')
    await ctx.channel.send(embed=mbed)


@bot.command()
async def bank_help(ctx):
    mbed = discord.Embed(title='**Skyblock Bot Bank Help**',
                         description='All Bank Commands',
                         color=discord.Color.from_rgb(255, 255, 255))
    fields = [
        ("?balance", "Opens An Account And Gives Account Balance", True),
        ("?withdraw [Amount]", "Withdraw Money From Your Bank", False),
        ("?deposit [Amount]", "Deposit Money In Your Bank", False),
        ("?send [Member]", "Send Money To A Specfific User", False),
        ("?invest [Amount]", "You've A 75% Chance Of Winning This", False),
        ("?slots [Amount]", "You've A 66% Chance Of Winning This", False),
        ("?adv [Amount]", "Takes 2hr To Complete Then Gives 35% Of The Money",
         False),
        ("If The Bot Doesn't Respond between The Time It Mentioned Then",
         "Then Do ?adv_clear to Get All Money Back", False)
    ]
    for name, value, inline in fields:
        mbed.add_field(name=name, value=value, inline=inline)
    mbed.set_thumbnail(
        url=
        'https://cdn.discordapp.com/attachments/822717749725757460/874358230199992360/unknown.png'
    )
    await ctx.channel.send(embed=mbed)


@bot.command()
async def level_help(ctx):
    mbed = discord.Embed(title="**Skyblock Leveling System Help**",
                         description="All Level Related Commands",
                         color=discord.Color.from_rgb(255, 255, 255))
    fields = [("?rank", "Shows Your Rank", True),
              ("?leaderboard", "Shows Top 10 People", False),
              ("?mk_poll [time] [question inside ""] [options upto 10 inside ""]", False)]
    for name, value, inline in fields:
        mbed.add_field(name=name, value=value, inline=inline)
    mbed.set_thumbnail(
        url=
        'https://cdn.discordapp.com/attachments/822717749725757460/874358230199992360/unknown.png'
    )
    await ctx.send(embed=mbed)

@bot.command()
async def all_commands(ctx):
  await ctx.send(""" set_birthday 
backgrounds
change_background    
  decrease_xp          
  increase_xp          
  leaderboard          
  mkpoll               
  rank                 
  adveq                
  change_playlist      
  connect              
  disconnect           
  eq                   
  get_playlist         
  lyrics               
  next                 
  pause                
  playing              
  previous             
  queue                
  repeat               
  restart              
  save_playlist        
  seek                 
  shuffle              
  skipto               
  stop                 
  volume               
  yt                   
  k                    
  add_account          
  add_mod              
  adv_clear            
  adventure            
  announcement_add     
  b_balance            
  balance              
  baltop               
  ban                  
  bank_help            
  botgoingdown         
  botonline            
  buy_role             
  change_channel_perm  
  check_for_embed      
  checking             
  clearADV             
  close_ticket         
  deposit              
  donate               
  g_roll               
  generate_gift_code   
  give_role            
  giveaway             
  h_h_hide             
  help                 Shows this message
  invest               
  kick                 
  level_help           
  load                 
  load_all_cogs        
  lock                 
  mod_help             
  music_help           
  mute                 
  over_server_lockdown 
  ping                 
  profile              
  rejoin_reqest        
  request_make         
  rollMLO              
  sb_help              
  self_role_custom     
  selfrole             
  send                 
  send_gift_code       
  server_lockdown      
  slots                
  sm                   
  temp_mute            
  unban                
  unload               
  unload_all_cogs      
  unlock               
  unmute               
  warn_user            
  withdraw             

Type ?help command for more info on a command.
You can also type ?help category for more info on a category.""")


#################################################### EXTRA COMMANDS


@bot.command()
async def botonline(ctx):
    valid_user = ['AdvicSaha#4896']

    if str(ctx.author) in valid_user:
        mbed = discord.Embed(title='Bot Now Online!',
                             description="Skyblock Bot Is Now Online!",
                             timestamp=datetime.utcnow(),
                             color=discord.Color.from_rgb(255, 255, 255))
        fields = [("Name", "Skyblock Bot", True),
                  ("Created By", "Advic Saha", True),
                  ("For Info", "Visit #Info", False),
                  ("For Commands", "?sb_help", True),
                  ("If Any Command Not Working Then", "Contact AdvicSaha#4896",
                   False)]

        for name, value, inline in fields:
            mbed.add_field(name=name, value=value, inline=inline)
        mbed.set_author(name='Advic Saha', icon_url=ctx.author.avatar_url)
        mbed.set_thumbnail(
            url=
            'https://cdn.discordapp.com/attachments/822717749725757460/874358230199992360/unknown.png'
        )
        await ctx.message.delete()
        await ctx.send(embed=mbed)
    else:
        await ctx.message.delete()
        await ctx.channel.send(
            f"{ctx.author.mention} You Don't Have Permission For This")


@bot.command()
async def botgoingdown(ctx):
    valid_users = ['AdvicSaha#4896']

    if str(ctx.author) in valid_users:
        mbed = discord.Embed(
            title='Bot Will Be Going Down In The Next Few Mins!',
            description='Bot Will Be Back Online Soon!',
            timestamp=datetime.utcnow(),
            color=discord.Color.from_rgb(255, 255, 255))
        mbed.set_thumbnail(
            url=
            'https://cdn.discordapp.com/attachments/822717749725757460/874358230199992360/unknown.png'
        )
        await ctx.message.delete()
        await ctx.channel.send(embed=mbed)
    else:
        msg = ctx.author.mention + ' ' + ' You Dont Have Permission For This'
        await ctx.message.delete()
        await ctx.channel.send(msg)


###############################################################  MOD COMMANDS


@bot.command()
async def sm(ctx, sm: int, channel=None):
    if channel is None:
        channel = ctx.channel
    if sm < 0:
        await ctx.send("Slow Mode Should be 0 or Positive")
        return
    else:
        await channel.edit(slowmode_delay=sm)


@bot.command()
@commands.has_permissions(manage_channels=True)
@commands.has_role("Bot-Mod")
async def lock(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send(f'Locked #{channel}')


@bot.command()
@commands.has_permissions(manage_channels=True)
@commands.has_role("Bot-Mod")
async def unlock(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send(f'Unlocked #{channel}')


@bot.command(name="server_lockdown")
@commands.has_permissions(manage_channels=True)
@commands.has_role("Bot-Mod")
async def change_server_lockdown(ctx):
    await ctx.message.delete()
    server_in_lockdown.remove(server_in_lockdown[0])
    server_in_lockdown.append("in_lockdown")
    no_change = ["873465171132166144", "873466841912213534", "875000973221838849", "875421282286592081", "875426157242220555", "875598583846559794", "878999525258330112", "883673096429654057", "904368580328579123", "904367921218863174", "914446001987801169", "905107008028565574", "904389665816207380", "904314846781268009", "904019281249959957"]
    for channel in ctx.guild.channels:
      if str(channel.id) in no_change:
          continue
      else:
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role,
                                      overwrite=overwrite)
    mbed = discord.Embed(
        title="The Syndicate Is In Complete Lockdown \ud83d\udd12",
        description="Server Has Been Went In Complete Lockdown",
        color=discord.Color.red())

    await ctx.send(embed=mbed)


@bot.command(name="over_server_lockdown")
@commands.has_permissions(manage_channels=True)
@commands.has_role("Bot-Mod")
async def server_lockdown(ctx):
    await ctx.message.delete()
    no_change = ["873465171132166144", "873466841912213534", "875000973221838849", "875421282286592081", "875426157242220555", "875598583846559794", "878999525258330112", "883673096429654057", "904368580328579123", "904367921218863174", "914446001987801169", "905107008028565574", "904389665816207380", "904314846781268009", "904019281249959957"]
    server_in_lockdown.remove(server_in_lockdown[0])
    server_in_lockdown.append("no-lockdown")
    for channel in ctx.guild.channels:
        if str(channel.id) in no_change:
          continue
        else:
          overwrite = channel.overwrites_for(ctx.guild.default_role)
          overwrite.send_messages = True
          await channel.set_permissions(ctx.guild.default_role,
                                        overwrite=overwrite)
    await ctx.send("Server is No More In Lockdown")

@bot.command()
@commands.has_role("Bot-Mod")
async def clear(ctx, number=None):
  await ctx.message.delete()
  if number is None:
    await ctx.send("Provide Some number", delete_after=5)
  else:
    if number == "all":
      count=0
      async for message in ctx.channel.history():
        count=count+1
        await message.delete()
    else:
      count=0
      async for message in ctx.channel.history(limit=int(number)+1):
        count=count+1
        await message.delete()

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):

    mods = []
    mod_role = discord.utils.get(ctx.guild.roles, name="Bot-Mod")

    for members in ctx.guild.members:
        if mod_role in members.roles:
            mods.append(members.name + '#' + members.discriminator)

    if str(ctx.author) in mods:
        if str(ctx.author) != member:
            if reason == None:
                reason = 'No Reason Provided'

            mbed = discord.Embed(
                title='You Have Been Kicked From **Syndicate* ',
                timestamp=datetime.utcnow(),
                color=discord.Color.red())
            fields = [("Reason", reason, True)]
            for name, value, inline in fields:
                mbed.add_field(name=name, value=value, inline=inline)

            await ctx.send(f'Kicked {member} for {reason}')
            try:
                await member.send(embed=mbed)
            except:
                pass
            await member.kick(reason=reason)
        else:
            await ctx.send(f"{ctx.author.mention} You Can't Kick YourSelf!")
    else:
        await ctx.channel.send(f"{member.mention} You're Not A Server-Mod")


@bot.command()
@commands.has_permissions(kick_members=True)
async def rejoin_reqest(ctx, member: discord.Member, *, reason=None):
    mods = []
    mod_role = discord.utils.get(ctx.guild.roles, name="Bot-Mod")

    for members in ctx.guild.members:
        if mod_role in members.roles:
            mods.append(members.name + '#' + members.discriminator)

    if str(ctx.author) in mods:
        if str(ctx.author) != member:
            if reason == None:
                reason = 'No Reason Provided'

            await ctx.send(f'Kicked {member} for {reason}')

            await member.send(
                "You Have Been Kicked From Syndicate Because Of An Unknown Error. Kindly Plz Join Back The Server. https://discord.gg/AZEA4azNwk"
            )

            await member.kick(reason=reason)
        else:
            await ctx.send(f"{ctx.author.mention} You Can't Kick YourSelf!")
    else:
        await ctx.channel.send(f"{member.mention} You're Not A Server-Mod")


@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):

    mods = []
    mod_role = discord.utils.get(ctx.guild.roles, name="Bot-Mod")

    for members in ctx.guild.members:
        if mod_role in members.roles:
            mods.append(members.name + '#' + members.discriminator)

    if str(ctx.author) in mods:
        if str(ctx.author) != member:
            if reason == None:
                reason = 'No Reason Provided'

            mbed = discord.Embed(
                title='You Have Been Banned From **Syndicate*',
                timestamp=datetime.utcnow(),
                color=discord.Color.red())
            fields = [("Reason", reason, True)]
            for name, value, inline in fields:
                mbed.add_field(name=name, value=value, inline=inline)

            await ctx.send(f'Banned {member} for {reason}')
            try:
                await member.send(embed=mbed)
            except:
                pass
            await member.ban(reason=reason)
        else:
            await ctx.channel.send(
                f"{ctx.author.mention} You Can't Ban YourSelf!")
    else:
        await ctx.channel.send(f"{member.mention} You're Not A Server-Mod")


@bot.command()
async def unban(ctx, member):

    mods = []
    mod_role = discord.utils.get(ctx.guild.roles, name="Bot-Mod")

    for members in ctx.guild.members:
        if mod_role in members.roles:
            mods.append(members.name + '#' + members.discriminator)

    if str(ctx.author) in mods:
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name,
                                                   member_discriminator):
                await ctx.guild.unban(user)
                await ctx.channel.send(
                    f'Unbanned {user.name}#{user.discriminator}')
                return
    else:
        await ctx.channel.send(f"{member.mention} You're Not A Server-Mod")


@bot.command(name="mute")
@commands.has_role("Bot-Mod")
async def mute(ctx, member: discord.Member, *, reason=None):
    if str(ctx.author) != member:
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name="Muted")

        if not mutedRole:
            mutedRole = await guild.create_role(name="Muted")

            for channel in guild.channels:
                await channel.set_permissions(mutedRole,
                                              speak=False,
                                              send_messages=False)

        mbed = discord.Embed(title='You Have Been Muted In **Syndicate*',
                             timestamp=datetime.utcnow(),
                             color=discord.Color.red())

        fields = [("Reason", reason, True)]
        for name, value, inline in fields:
            mbed.add_field(name=name, value=value, inline=inline)

        await member.add_roles(mutedRole, reason=reason)
        await ctx.send(f'Muted {member.mention} for reason {reason}')
        await member.send(embed=mbed)
    else:
        await ctx.channel.send(f"{member.mention} You Can't Mute Yourself!")


@bot.command()
async def unmute(ctx, member: discord.Member):

    mods = []
    mod_role = discord.utils.get(ctx.guild.roles, name="Bot-Mod")

    for members in ctx.guild.members:
        if mod_role in members.roles:
            mods.append(members.name + '#' + members.discriminator)

    if str(ctx.author) in mods:
        mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

        mbed = discord.Embed(title='You Have Been Unmuted In **Syndicate*',
                             timestamp=datetime.utcnow(),
                             color=discord.Color.red())

        await member.remove_roles(mutedRole)
        await ctx.send(f'Unmuted {member.mention}')
        await member.send(embed=mbed)
    else:
        await ctx.channel.send(f"{member.mention} You're Not A Server-Mod")


@bot.command()
async def temp_mute(ctx, member: discord.Member, t: int, mode="s"):
    mods = []
    mod_role = discord.utils.get(ctx.guild.roles, name="Bot-Mod")

    for members in ctx.guild.members:
        if mod_role in members.roles:
            mods.append(members.name + '#' + members.discriminator)

    if str(ctx.author) in mods:
        mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
        time = Time.convert_time(t, mode)

        mbed = discord.Embed(
            title=f"You're Temporary Muted In **SyndicateFor {time}sec**",
            timestamp=datetime.utcnow(),
            color=discord.Color.from_rgb(255, 255, 255))

        mbed2 = discord.Embed(
            title=f"You're Not Anymore Muted In **Syndicate*",
            timestamp=datetime.utcnow(),
            color=discord.Color.from_rgb(255, 255, 255))

        mbed3 = discord.Embed(title=f"Muted {member} For {time}sec",
                              timestamp=datetime.utcnow(),
                              color=discord.Color.red())

        mbed4 = discord.Embed(title=f"Unmuted {member}",
                              timestamp=datetime.utcnow(),
                              color=discord.Color.red())

        await member.add_roles(mutedRole)
        await member.send(embed=mbed)
        await ctx.send(embed=mbed3)

        await asyncio.sleep(time)

        await member.send(embed=mbed2)
        await ctx.send(embed=mbed4)
        await member.remove_roles(mutedRole)

    else:
        await ctx.send(f"{ctx.author.mention} You're Not A Server-Mod!")


@bot.command()
async def warn_user(ctx, member: discord.Member, *, reason=None):
    print(member)

    mods = []
    mods_role = discord.utils.get(ctx.guild.roles, name="Bot-Mod")

    for m in ctx.guild.members:
        if mods_role in m.roles:
            mods.append(m.name + '#' + m.discriminator)

    if str(ctx.author) in mods:
        try:
            mbed = discord.Embed(title='You Have Been Warned ',
                                 color=discord.Color.red())
            fields = [("Reason", reason, True)]
            for name, value, inline in fields:
                mbed.add_field(name=name, value=value, inline=inline)
            await member.send(embed=mbed)
            await ctx.channel.send(member.mention + ' Has Been Warned!')
        except:
            await ctx.channel.send("Couldn't Dm The Given User")
    else:
        await ctx.channel.send(ctx.author.mention +
                               ' You Need To Be A Server-Mod For This')


@bot.command()
async def add_mod(ctx, member: discord.Member):

    mods = []
    mods_role = discord.utils.get(ctx.guild.roles, name="Bot-Mod")

    for m in ctx.guild.members:
        if mods_role in m.roles:
            mods.append(m.name + '#' + m.discriminator)

    if str(ctx.author) in mods:
        mbed = discord.Embed(
            title="You Have Been Added As A Mod",
            description="You're A Mod Now In **Skyblock Server**",
            timestamp=datetime.utcnow(),
            color=discord.Color.from_rgb(255, 255, 255))

        await member.add_roles(mods_role)
        await ctx.send(f"Added {member} As A Mod")
        await member.send(embed=mbed)
        print(f"Added {member} As A Mod")
    else:
        await ctx.send(f"{ctx.author.mention} You're Not A Server Mod")


@bot.command()
@commands.has_role("Bot-Mod")
async def give_role(ctx, member: discord.Member, role):
    role = discord.utils.get(ctx.guild.roles, name=role)
    print(role)

    await member.add_roles(role)
    await ctx.send(f"{role} Given To {member}")


@bot.command()
@commands.has_role("Bot-Mod")
async def change_channel_perm(ctx, role: str):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name=role)

    for channel in guild.channels:
        await channel.set_permissions(mutedRole,
                                      speak=False,
                                      send_messages=False,
                                      view_channel=False)

    await ctx.send("Changed Perms")


##################################################### Bank

@bot.command(name="b_balance", aliases=["bbal"])
async def bank_balance(ctx):
  users = await get_bank_data()

  mbed=discord.Embed(
    title=f"Server's Bank Balance: {users[str(ctx.guild.id)]['bank']}",
    color=discord.Color.from_rgb(255, 153, 51)
  )
  await ctx.send(embed=mbed)

@bot.command(name="balance", aliases=["bal"])
async def balance(ctx, target: Optional[discord.Member]):
    author = target or ctx.author
    Economy.open_account(author)
    user = author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    mbed = discord.Embed(title=f"{author}'s Account Balance: ",
                         color=discord.Color.from_rgb(255, 153, 51))
    fields = [("Wallet: ", wallet_amt, True), ("Bank: ", bank_amt, True)]

    for name, value, inline in fields:
        mbed.add_field(name=name, value=value, inline=inline)

    await ctx.send(embed=mbed)


@bot.command(name="withdraw", aliases=["wit"])
async def withdraw(ctx, amount=None):
    Economy.open_account(ctx.author)

    if amount == None:
        await ctx.send("Please Enter The Amount")
        return

    if amount == "all":
        data = await get_bank_data()
        amount = data[str(ctx.author.id)]["bank"]

    bal = Economy.update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[1]:
        await ctx.send("You Don't Have Enough Coin!")
        return

    if amount < 0:
        await ctx.send("Amount Must Be Positive!")

    Economy.update_bank(ctx.author, amount)
    Economy.update_bank(ctx.author, -1 * amount, "bank")

    users = await get_bank_data()

    wallet_amt = users[str(ctx.author.id)]["wallet"]
    bank_amt = users[str(ctx.author.id)]["bank"]

    mbed = discord.Embed(title=f"**You Just Withdrew {amount} Coins!**",
                         color=discord.Color.from_rgb(255, 153, 51))
    fields = [("Your Current Bank Balance: ", "----", False),
              ("Wallet: ", wallet_amt, False), ("Bank: ", bank_amt, True)]

    for name, value, inline in fields:
        mbed.add_field(name=name, value=value, inline=inline)

    await ctx.send(embed=mbed)


@bot.command(name="deposit", aliases=["dep"])
async def deposit(ctx, amount=None):
    Economy.open_account(ctx.author)

    if amount == None:
        await ctx.send("Please Enter The Amount")
        return

    if amount == "all":
        data = await get_bank_data()
        amount = data[str(ctx.author.id)]["wallet"]

    bal = Economy.update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send("You Don't Have Enough Coin!")
        return

    if amount < 0:
        await ctx.send("Amount Must Be Positive!")

    Economy.update_bank(ctx.author, -1 * amount)
    Economy.update_bank(ctx.author, amount, "bank")

    users = await get_bank_data()

    wallet_amt = users[str(ctx.author.id)]["wallet"]
    bank_amt = users[str(ctx.author.id)]["bank"]

    mbed = discord.Embed(title=f"**You Just Deposited {amount} Coins!**",
                         color=discord.Color.from_rgb(255, 153, 51))
    fields = [("Your Current Bank Balance: ", "----", False),
              ("Wallet: ", wallet_amt, False), ("Bank: ", bank_amt, True)]

    for name, value, inline in fields:
        mbed.add_field(name=name, value=value, inline=inline)

    await ctx.send(embed=mbed)


@bot.command()
async def baltop(ctx, x=5):
    users = await get_bank_data()
    leaderboard = {}
    total = []

    for user in users:
        if not users[user]['type'] == "guild":
            if users[user]['hide'] == 0:
                name = int(user)
                total_amount = users[user]["wallet"] + users[user]["bank"]
                leaderboard[total_amount] = name
                total.append(total_amount)

    total = sorted(total, reverse=True)

    mbed = discord.Embed(
        title=f"Top {x} Richest People In **Syndicate*",
        description=
        f"Server's Bank Balance: {users[str(ctx.guild.id)]['bank']}",
        color=discord.Color.from_rgb(255, 153, 51))

    index = 1

    for amt in total:
        id_ = leaderboard[amt]
        member = bot.get_user(id_)
        if member is not None:
            name = member.name
            mbed.add_field(name=f"{index}. {name}",
                           value=f"{amt}",
                           inline=False)
            if index == x:
                break
            else:
                index += 1

    await ctx.send(embed=mbed)


@bot.command()
async def send(ctx, member: discord.Member, amount=None):
    Economy.open_account(ctx.author)
    Economy.open_account(member)

    if amount == None:
        await ctx.send("Please Enter The Amount")
        return

    bal = Economy.update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[1]:
        await ctx.send("You Don't Have Enough Coin!")
        return

    if amount < 0:
        await ctx.send("Amount Must Be Positive!")

    tax = round(0.02 * amount)
    amount = amount - tax

    Economy.update_bank_using_id(ctx.guild.id, tax, "bank")
    Economy.update_bank(ctx.author, -1 * amount, "bank")
    Economy.update_bank(member, amount, "bank")

    await ctx.send(
        f"You Just Gave {member} {amount} Coins! \n *2% of your transaction has been deducted for server's bank*"
    )


@bot.command(name="adventure", aliases=["adv"])
async def adv(ctx, amount, bl="false"):
    Economy.open_account(ctx.author)
    adv = adv_db.find_one({"id": ctx.author.id})
    user = ctx.author.name + "#" + ctx.author.discriminator

    if adv is None:
        newuser = {"id": ctx.author.id, "adv": False, "mLO": 0}
        adv_db.insert_one(newuser)
        await ctx.send("Created Account, Plz Try Sending This Command Again :D")
    else:
        adv_value = adv["adv"]

        if adv_value == True:
            await ctx.send(
                f"{ctx.author.mention}, You're Already On An Adventure Try Again Once You're Back From The Adventure!"
            )
        elif user in adv_people:
            await ctx.send("You're Already On An Adventure")
        else:
            if bl == "true":
              checking_amount = int(amount)+20000000
            else:
              checking_amount = int(amount)

            if amount == None:
                await ctx.send("Please Enter The Amount")
                return

            bal = Economy.update_bank(ctx.author)

            amount = int(amount)

            if checking_amount > bal[0]:
                await ctx.send("You Don't Have Enough Coin!")
                return

            if amount < 0:
                await ctx.send("Amount Must Be Positive!")
                return

            if amount > 100000000:
                await ctx.send("Can't Go On An Adventure With More Than 100M!")
                return

            if amount <= 500000:
                waiting_time = 1800
                text = "30 Min"

            if amount > 500000 and amount <= 1000000:
                waiting_time = 3600
                text = "1 Hr"

            if amount > 1000000 and amount <= 10000000:
                waiting_time = 7200
                text = "2 Hr"
            
            if amount > 10000000 and amount <= 100000000:
              waiting_time = 14400
              text = "4 Hr"

            if amount == 1:
                waiting_time = 2
                text = "IDK LOL"

            adv_db.update_one({"id": ctx.author.id}, {"$set": {"adv": True}})
            adv_db.update_one({"id": ctx.author.id}, {"$set": {"mLO": amount}})

            await ctx.send(
                f"{ctx.author.mention}, Going On An Adventure With {amount} SB Coins For {text}!"
            )
            Economy.update_bank(ctx.author, -1 * amount)
            if bl == "true":
              Economy.update_bank(ctx.author, -1 * int(20000000))
              Economy.update_bank_using_id(ctx.guild.id, int(20000000), "bank")
            adv_people.append(user)
            await asyncio.sleep(waiting_time)
            ran = random.randint(0, 100)
            adv_db.update_one({"id": ctx.author.id}, {"$set": {"adv": False}})
            adv_people.remove(user)
            if ran == 0:
                await ctx.send(
                    f"{ctx.author.mention}, You're Back From The Adventure But You Found Nothing :'("
                )
                adv_db.update_one({"id": ctx.author.id}, {"$set": {"mLO": 0}})
                Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
            else:
                if bl == "true":
                  rate = random.randint(120, 160)
                else:
                  rate = random.randint(50, 80)
                w_amount = (rate * amount) / 100
                t_amount = round(w_amount + amount)
                tax = round(t_amount * 0.05)
                t_amount = t_amount - tax
                adv_db.update_one({"id": ctx.author.id}, {"$set": {"mLO": 0}})
                Economy.update_bank_using_id(ctx.guild.id, tax, "bank")
                Economy.update_bank(ctx.author, t_amount)
                await ctx.send(
                    f"{ctx.author.mention}, You're Back From The Adventure And You Found {t_amount} SB Coins! \n *10% has been deducted from your total amount for server's bank*"
                )


@bot.command()
async def rollMLO(ctx):
    user = ctx.author.name + "#" + ctx.author.discriminator
    if not user in adv_people:
        adv = adv_db.find_one({"id": ctx.author.id})
        mlo = adv["mLO"]
        if mlo == 0:
            await ctx.send("You Don't Have Any Coins In DB")
        else:
            adv_db.update_one({"id": ctx.author.id}, {"$set": {"mLO": 0}})
            await ctx.send(f"You Had {mlo} Coins In DB")
            Economy.update_bank(ctx.author, mlo, "wallet")
    else:
        await ctx.send("You're On An Adventure Try Once you're back!")


@bot.command()
async def clearADV(ctx, member: Optional[discord.Member]):
    target = member or ctx.author
    adv = adv_db.find_one({"id": target.id})

    if adv is None:
        if ctx.author == target:
            await ctx.send("You Don't Have A DB")
        else:
            await ctx.send(f"{target} Don't Have A DB")
        return

    current_adv = adv["adv"]
    if current_adv == True:
        adv_db.update_one({"id": target.id}, {"$set": {"adv": False}})
        changed_value = "False"
    else:
        adv_db.update_one({"id": target.id}, {"$set": {"adv": True}})
        changed_value = "True"

    await ctx.send(f"Changed Value For {target} To {changed_value}!")


@bot.command()
async def adv_clear(ctx, member: Optional[discord.Member]):
    target = member or ctx.author
    if target in adv_people:
      await ctx.send("You're Already on An Adventure")
    else:
      adv = adv_db.find_one({"id": target.id})

      if adv is None:
          if ctx.author == target:
              await ctx.send("You Don't Have A DB")
          else:
              await ctx.send(f"{target} Don't Have A DB")
          return

      current_adv = adv["adv"]
      if current_adv == True:
          adv_db.update_one({"id": target.id}, {"$set": {"adv": False}})
      else:
          adv_db.update_one({"id": target.id}, {"$set": {"adv": True}})

      mlo = adv["mLO"]
      if mlo == 0:
          await ctx.send("Nothing Found")
      else:
          adv_db.update_one({"id": ctx.author.id}, {"$set": {"mLO": 0}})
          await ctx.send(f"You Had {mlo} Coins In DB And Cleared ADV")
          Economy.update_bank(ctx.author, mlo, "wallet")


@bot.command(name="invest", aliases=["inv"])
async def inv(ctx, amount=None):

    Economy.open_account(ctx.author)

    if amount == None:
        await ctx.send("Please Enter The Amount")
        return

    bal = Economy.update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send("You Don't Have Enough Coin!")
        return

    if amount < 0:
        await ctx.send("Amount Must Be Positive!")

    Economy.update_bank(ctx.author, -1 * amount)

    random_num = random.randint(-25, 55)

    if random_num <= 0:
        await ctx.send('You Just Lost Your Investment')
        Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
        return

    if random_num > 0:
        tax = round(0.02 * amount)
        amount = amount - tax
        rate = random.randint(45, 55)
        profit = (rate * amount) / 100
        total_amount = round(amount + profit)
        Economy.update_bank_using_id(ctx.guild.id, tax, "bank")
        Economy.update_bank(ctx.author, total_amount, "wallet")
        mbed = discord.Embed(
            title=f"{ctx.author} Just Got A Profit Of {round(profit)} Coins!",
            color=discord.Color.from_rgb(255, 153, 51))
        await ctx.send(embed=mbed)


@bot.command()
async def slots(ctx, amount=None):
    Economy.open_account(ctx.author)

    if amount == None:
        await ctx.send("Please Enter The Amount")
        return

    bal = Economy.update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send("You Don't Have Enough Coin!")
        return

    if amount < 0:
        await ctx.send("Amount Must Be Positive!")
        return

    if amount > 100000:
      await ctx.send("The amount should be less than 100k")
      return 

    Economy.update_bank(ctx.author, -1 * amount)

    final = []
    for i in range(3):
        a = random.choice(["X", "Y", "Z"])
        final.append(a)

    if final[0] == final[1] == final[2]:
        tax=round(amount*0.1)
        amount=amount-tax
        Economy.update_bank(ctx.author, 5 * amount)
        users = await get_bank_data()
        total_amt = users[str(ctx.author.id)]["wallet"]
        mbed = discord.Embed(title=str(final)[1:-1],
                             color=discord.Color.from_rgb(255, 153, 51))
        mbed.add_field(name=f"{ctx.author} Just Won {amount*10} Coins!",
                       value=f"Your Wallet Balance: {total_amt}",
                       inline=True)
        await ctx.send(embed=mbed)
    elif final[0] == final[1] or final[1] == final[2] or final[2] == final[0]:
        tax=round(amount*0.1)
        amount=amount-tax
        Economy.update_bank(ctx.author, 2 * amount)
        users = await get_bank_data()
        total_amt = users[str(ctx.author.id)]["wallet"]
        mbed = discord.Embed(title=str(final)[1:-1],
                             color=discord.Color.from_rgb(255, 153, 51))
        mbed.add_field(name=f"{ctx.author} Just Won {amount*5} Coins!",
                       value=f"Your Wallet Balance: {total_amt}",
                       inline=True)
        await ctx.send(embed=mbed)
    else:
        mbed = discord.Embed(title=str(final)[1:-1],
                             color=discord.Color.from_rgb(255, 153, 51))
        users = await get_bank_data()
        total_amt = users[str(ctx.author.id)]["wallet"]
        users[str(ctx.guild.id)]['bank'] += amount

        with open("jsons/mainBank.json") as f:
          json.dump(users, f)

        mbed.add_field(name=f"You Lost {amount} Coins",
                       value=f"Your Wallet Balance: {total_amt}",
                       inline=True)
        await ctx.send(embed=mbed)


@bot.command()
async def buy_role(ctx, role: discord.Role):
    Economy.open_account(ctx.author)

    if role == None:
        await ctx.send("Please Enter A Role To Buy")
        return

    lower_role = get(ctx.guild.roles, name="Lower-Class")
    middle_role = get(ctx.guild.roles, name="Middle-Class")
    upper_role = get(ctx.guild.roles, name="Upper-Class")
    VIP_role = get(ctx.guild.roles, name="VIP")
    VIP1 = get(ctx.guild.roles, name="VIP+")
    VIP2 = get(ctx.guild.roles, name="VIP++")
    VIP3 = get(ctx.guild.roles, name="VIP+++")
    SuperVIP = get(ctx.guild.roles, name="Super-VIP")
    SuperVIP1 = get(ctx.guild.roles, name="Super-VIP+")
    SuperVIP2 = get(ctx.guild.roles, name="Super-VIP++")
    SuperVIP3 = get(ctx.guild.roles, name="Super-VIP+++")
    SuperMVP2 = get(ctx.guild.roles, name="Super-Duper-MVP+++")
    SBDOUBLE = get(ctx.guild.roles, name="SB-DOUBLE")

    bal = Economy.update_bank(ctx.author)

    if role == lower_role:
        amount = int(5000)
        if amount < bal[0]:
            Economy.update_bank(ctx.author, -1 * amount)
            await ctx.author.add_roles(role)
            await ctx.send("You Just Bought Lower-Class Role!")
            return
        else:
            await ctx.send("You Don't Have Enough Coins")

    if role == middle_role:
        amount = int(7000)
        if amount < bal[0]:
            Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
            Economy.update_bank(ctx.author, -1 * amount)
            await ctx.author.add_roles(role)
            await ctx.send("You Just Bought Middle-Class Role!")
            return
        else:
            await ctx.send("You Don't Have Enough Coins")

    if role == upper_role:
        amount = int(10000)
        if amount < bal[0]:
            Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
            Economy.update_bank(ctx.author, -1 * amount)
            await ctx.author.add_roles(role)
            await ctx.send("You Just Bought Upper-Class Role!")
            return
        else:
            await ctx.send("You Don't Have Enough Coins")

    if role == VIP_role:
        amount = int(15000)
        if amount < bal[0]:
            Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
            Economy.update_bank(ctx.author, -1 * amount)
            await ctx.author.add_roles(role)
            await ctx.send("You Just Bought VIP Role!")
            return
        else:
            await ctx.send("You Don't Have Enough Coins")

    if role == VIP1:
        amount = int(17000)
        if amount < bal[0]:
            Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
            Economy.update_bank(ctx.author, -1 * amount)
            await ctx.author.add_roles(role)
            await ctx.send("You Just Bought VIP+ Role!")
            return
        else:
            await ctx.send("You Don't Have Enough Coins")

    if role == VIP2:
        amount = int(20000)
        if amount < bal[0]:
            Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
            Economy.update_bank(ctx.author, -1 * amount)
            await ctx.author.add_roles(role)
            await ctx.send("You Just Bought VIP++ Role!")
            return
        else:
            await ctx.send("You Don't Have Enough Coins")

    if role == VIP3:
        amount = int(23000)
        if amount < bal[0]:
            Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
            Economy.update_bank(ctx.author, -1 * amount)
            await ctx.author.add_roles(role)
            await ctx.send("You Just Bought VIP+++ Role!")
            return
        else:
            await ctx.send("You Don't Have Enough Coins")

    if role == SuperVIP:
        amount = int(25000)
        if amount < bal[0]:
            Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
            Economy.update_bank(ctx.author, -1 * amount)
            await ctx.author.add_roles(role)
            await ctx.send("You Just Bought SuperVIP Role!")
            return
        else:
            await ctx.send("You Don't Have Enough Coins")

    if role == SuperVIP1:
        amount = int(30000)
        if amount < bal[0]:
            Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
            Economy.update_bank(ctx.author, -1 * amount)
            await ctx.author.add_roles(role)
            await ctx.send("You Just Bought Super-VIP+ Role!")
            return
        else:
            await ctx.send("You Don't Have Enough Coins")

        if role == SuperVIP2:
            amount = int(35000)
            if amount < bal[0]:
                Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
                Economy.update_bank(ctx.author, -1 * amount)
                await ctx.author.add_roles(role)
                await ctx.send("You Just Bought Super-VIP++ Role!")
                return
            else:
                await ctx.send("You Don't Have Enough Coins")

    if role == SuperVIP3:
        amount = int(40000)
        if amount < bal[0]:
            Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
            Economy.update_bank(ctx.author, -1 * amount)
            await ctx.author.add_roles(role)
            await ctx.send("You Just Bought Super-VIP+++ Role!")
            return
        else:
            await ctx.send("You Don't Have Enough Coins")

    if role == SuperMVP2:
        amount = int(100000)
        if amount < bal[0]:
            Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
            Economy.update_bank(ctx.author, -1 * amount)
            await ctx.author.add_roles(role)
            await ctx.send("You Just Bought Super-Duper-MVP+++ Role!")
            return
        else:
            await ctx.send("You Don't Have Enough Coins")

    if role == SBDOUBLE:
        amount = int(1000000)
        if amount < bal[0]:
            Economy.update_bank_using_id(ctx.guild.id, amount, "bank")
            Economy.update_bank(ctx.author, -1 * amount)

            with open("jsons/mainBank.json", "r") as f:
              data = json.load(f)
            data[str(ctx.author.id)]['sb']=1
            with open("jsons/mainBank.json", "w") as f:
              json.dump(data, f)

            await ctx.send(
                "You Just Bought **SB-DOUBLE Role!** From Now You'll Earn x20 Times The Money You Usually Earn On Message"
            )
            return
        else:
            await ctx.send("You Don't Have Enough Coins")


@bot.command()
@commands.has_role("Bot-Mod")
async def h_h_hide(ctx):
    users = await get_bank_data()

    if users[str(ctx.author.id)]['hide'] == 0:
        users[str(ctx.author.id)]['hide'] = 1
    else:
        users[str(ctx.author.id)]['hide'] = 0

    with open("jsons/mainBank.json", "w") as f:
        json.dump(users, f)


async def open_account(user):
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]['wallet'] = 0
        users[str(user.id)]['bank'] = 100
        users[str(user.id)]['hide'] = 0
        users[str(user.id)]['sb'] = 0

    with open("jsons/mainBank.json", "w") as f:
        json.dump(users, f)

    return True


async def openADV(user):
    val = await get_bank_data()

    if str(user.id) in val:
        return True
    else:
        val[str(user.id)] = {}
        val[str(user.id)]['adv'] = "t"

    with open("jsons/mainBank.json", "w") as f:
        json.dump(val, f)

    return True


async def getADVdetails():
    with open("jsons/adventure.json", "r") as f:
        val = json.load(f)

    return val


async def get_bank_data():
    with open("jsons/mainBank.json", "r") as f:
        users = json.load(f)

    return users


async def update_bank(user, change=0, mode="wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("jsons/mainBank.json", "w") as f:
        json.dump(users, f)

    bal = [users[str(user.id)]['wallet'], users[str(user.id)]['bank']]

    return bal


@bot.command()
async def donate(ctx, amount: int):
    Economy.open_account(ctx.author)
    bal = Economy.update_bank(ctx.author)

    if amount > bal[0]:
        await ctx.send(
            "You Don't Have Enough Coins! \n *you need to have the coins in your wallet*"
        )
        return
    Economy.update_bank(ctx.author, -1 * amount, "wallet")
    Economy.update_bank_using_id(ctx.guild.id, amount, "bank")

    await ctx.send(
        "Thank You For Donating! The Coins has been added to server's bank")


########################################################################### MINECRAFT ACCOUNT VERIFICATION


@bot.command()
async def add_account(ctx, mc_username: str, aternos_username: str):
    channel = bot.get_channel(904374369340502087)
    mbed = discord.Embed(
        title=f"**ATERNOS WHITELIST AND SERVER START ACCESS**",
        description=f"{ctx.author} ; {mc_username} ; {aternos_username}")
    mbed.set_footer(text="REACT WITH \u2705 ONCE ADDED!")
    msg = await channel.send("<@everyone>", embed=mbed)
    await msg.add_reaction("\u2705")
    with open("jsons/selfroles.json", "r") as f:
        self_roles = json.load(f)

    self_roles[str(msg.id)] = {}
    self_roles[str(msg.id)]['emojis'] = "\u2705"
    self_roles[str(msg.id)]['roles'] = "NONE"
    self_roles[str(msg.id)]['work'] = "minecraft_account_verification"
    self_roles[str(msg.id)]['user'] = ctx.author.id

    with open("jsons/selfroles.json", "w") as f:
        json.dump(self_roles, f)

    await ctx.send(
        "Sent Request To The Mods!; Plz Wait For Some Time To Be Added In The Server"
    )


@bot.command()
async def close_ticket(ctx, ticket_number: str, member: discord.Member, *, message=None):
    with open("jsons/tickets_info.json", "r") as f:
        data = json.load(f)

    for ticket in data:
        if data[ticket]['ticket_number'] == ticket_number:
            if message is None:
              message = "No Message Provided"

            userid = ticket
            user = bot.get_user(int(userid))
            print(user)
            role = discord.utils.get(ctx.author.guild.roles,
                                     name="Active-Ticket")
            await member.remove_roles(role)
            del data[ticket]
            with open("jsons/tickets_info.json", "w") as f:
                json.dump(data, f)
            await ctx.send(f"Ticket Number: {ticket_number} was Closed")
            await user.send(f"Your Ticket Was Closed, Message From Mod: **{message}**")
            break

@bot.command()
@commands.has_role("Bot_Mod")
async def change_status(ctx, type: str, *, message: str):
  if type == "PLAYING":
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing, name=message))
  elif type == "WATCHING":
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name=message))
  elif type == "LISTENING":
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name=message))
  else:
    await ctx.send("Invalid type")

############################################################################ GIVEAWAY COMMANDS!


@bot.command()
@commands.has_role("self_role")
async def giveaway(ctx):
    await ctx.send("Answer The Question In Next Min!")

    questions = [
        "Enter Channel: ", "Enter Duration: ",
        "This Event Is Getting Sponsored By (Enter Id Of That User):  ",
        "Enter Prize: "
    ]

    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    for i in questions:
        await ctx.send(i)

        try:
            msg = await bot.wait_for('message', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Better Type Faster Next Time!")
            return
        else:
            answers.append(msg.content)

    duration = answers[1]
    time = Time.convert_time_direct(duration)
    prize = answers[3]
    sponser = answers[2]
    user = bot.get_user(int(sponser))
    c_id = int(answers[0][2:-1])
    channel = bot.get_channel(c_id)

    mbed = discord.Embed(title=f"**Giveaway Hosted By {ctx.author.name}**",
                         description=f"**Prize: {prize}**",
                         color=discord.Color.from_rgb(255, 255, 255))
    mbed.add_field(name=f"Ending In {duration}",
                   value=f"**React With 🎉 To Enter Giveaway**",
                   inline=False)
    bot_msg = await channel.send("@everyone ", embed=mbed)
    await bot_msg.add_reaction("🎉")

    await asyncio.sleep(time)

    new_msg = await channel.fetch_message(bot_msg.id)

    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(bot.user))

    winner = random.choice(users)
    await channel.send(
        f"Congratulations! {winner.mention} Just Won **{prize}**!")
    await new_msg.delete()


@bot.command()
@commands.has_role("self_role")
async def g_roll(ctx, msg_id, *, prize):
    await ctx.message.delete()
    new_msg = await ctx.channel.fetch_message(msg_id)

    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(bot.user))

    winner = random.choice(users)
    await ctx.send(f"Congratulations! {winner.mention} Just Won **{prize}**!")


@bot.command()
@commands.has_role("Bot-Mod")
async def generate_gift_code(ctx, value):
    data = requests.get(f"https://a.advic.repl.co/generate_code?w={value}")
    code = data.text
    await ctx.send(f"<{code}>")


@bot.command()
@commands.has_role("Bot-Mod")
async def send_gift_code(ctx, value, user: discord.Member):
    data = requests.get(f"https://a.advic.repl.co/generate_code?w={value}")
    code = data.text
    await user.send(f"Your Code Worth: {value}. Code: <{code}>")
    await ctx.author.send(
        f"Sent Code To {user.name}. Worth: {value}. Code: <{code}>")


############################################################################ SELF ROLES!


@bot.command()
async def profile(ctx, member: discord.Member):
    mbed = discord.Embed(color=discord.Color.dark_teal())
    mbed.set_image(url=member.avatar_url)

    await ctx.send(embed=mbed)


@bot.command(name="selfrole")
@commands.has_role("self_role")
async def self_role(ctx):
    questions = [
        "Enter The Message: ", "Enter The Emojis: ",
        "Enter The Roles You Wanna Give: ", "Enter Channel: "
    ]

    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    for i in questions:
        await ctx.send(i)

        try:
            msg = await bot.wait_for('message', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Better Type Faster Next Time!")
            return
        else:
            answers.append(msg.content)

    emojis = answers[1].split(" ")
    roles = answers[2].split(" ")
    c_id = int(answers[3][2:-1])
    channel = bot.get_channel(c_id)

    mbed = discord.Embed(
        title="Create Ticket \ud83d\udce9",
        description="React With \ud83d\udce9 To Create New Ticket!",
        color=discord.Color.from_rgb(255, 255, 255))

    bot_msg = await channel.send(answers[0])

    with open("jsons/selfroles.json", "r") as f:
        self_roles = json.load(f)

    self_roles[str(bot_msg.id)] = {}
    self_roles[str(bot_msg.id)]['emojis'] = emojis
    self_roles[str(bot_msg.id)]['roles'] = roles
    self_roles[str(bot_msg.id)]['work'] = "self_role"

    with open("jsons/selfroles.json", "w") as f:
        json.dump(self_roles, f)

    for emoji in emojis:
        await bot_msg.add_reaction(emoji)


@bot.command()
async def self_role_custom(ctx):

    questions = [
        "Enter The Message: ", "Enter The Emojis: ",
        "Enter The Roles You Wanna Give: ", "Enter Channel: "
    ]

    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    for i in questions:
        await ctx.send(i)

        try:
            msg = await bot.wait_for('message', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Better Type Faster Next Time!")
            return
        else:
            answers.append(msg.content)

    emojis = [
        "<a:3496_Minecraft:918141735224369212>",
        "<a:amoungus:918141735471841280>", "<a:umbreon:918141735287291934>",
        "<:valorant:918141735102742538>", "<:Chess:883412790717612092>",
        "<:pencil_123:921452880936972338>"
    ]
    roles = answers[2].split(" ")
    c_id = int(answers[3][2:-1])
    channel = bot.get_channel(c_id)

    mbed = discord.Embed(
        title="Create Ticket \ud83d\udce9",
        description="React With \ud83d\udce9 To Create New Ticket!",
        color=discord.Color.from_rgb(255, 255, 255))
    message = "**Games** \n React To Get Roles!! \n\n <a:3496_Minecraft:918141735224369212>: <@&883637299953414144> \n\n <a:amoungus:918141735471841280>: <@&883675647682179124> \n\n <a:umbreon:918141735287291934>: <@&921458944482869319> \n\n <:valorant:918141735102742538>: <@&883637341179215913> \n\n <:Chess:883412790717612092>: <@&883672942351896586> \n\n <:pencil_123:921452880936972338>: <@&883637393746432030>"

    #bot_msg = await channel.send(answers[0])
    bot_msg = await channel.send(message)

    with open("jsons/selfroles.json", "r") as f:
        self_roles = json.load(f)

    self_roles[str(bot_msg.id)] = {}
    self_roles[str(bot_msg.id)]['emojis'] = emojis
    self_roles[str(bot_msg.id)]['roles'] = roles
    self_roles[str(bot_msg.id)]['work'] = "self_role"

    with open("jsons/selfroles.json", "w") as f:
        json.dump(self_roles, f)

    for emoji in emojis:
        await bot_msg.add_reaction(emoji)


@bot.event
async def on_raw_reaction_add(payload):
  if server_in_lockdown[0] == "in_lockdown":
    await payload.member.send("Server Is In Complete Lockdown Because Of Which You Won't Be Able to Use **Verfication, Self Roles, Requests, Tickets, And etc**")
  else:
    msg_id = payload.message_id

    with open("jsons/selfroles.json", "r") as f:
        self_roles = json.load(f)

        if payload.member.bot:
            return

    if str(msg_id) in self_roles:
        emojis = []
        roles = []

        for emoji in self_roles[str(msg_id)]["emojis"]:
            emojis.append(emoji)

        for role in self_roles[str(msg_id)]["roles"]:
            roles.append(role)

        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
        g = bot.get_guild(guild_id)

        print(emojis)
        print("choosed Emoji: ", payload.emoji)

        for i in range(len(emojis)):
            choosed_emoji = str(payload.emoji)
            if choosed_emoji == str(emojis[i]):
                print(roles[i])
                selected_role = roles[i]
                r = discord.utils.get(g.roles, name=selected_role)
                if str(msg_id) == "904020582184648724":
                    r2 = discord.utils.get(g.roles, name="Non-Verified")
                    await payload.member.remove_roles(r2)
                    await payload.member.add_roles(r)
                    await payload.member.send("You're Now Verified!")
                    await payload.member.send(
                        "To Join Our Minecraft Server:- do **?add_account [your minecraft account username] [your aternos account username]** in the bot dm and wait for some time to get added in the server (you'll get notified once you're added) visit <#904368580328579123> for more information!"
                    )
                elif self_roles[str(msg_id)]["work"] == "ticket":
                    ticket_number = General.make_new_ticket(payload.member.id)
                    if ticket_number == "0":
                        await payload.member.send(
                            "You Already Have One Ticket Open. Contact Server-Mods If not Open"
                        )
                    else:
                        role = discord.utils.get(g.roles, name="Active-Ticket")
                        await payload.member.add_roles(role)
                        channel = bot.get_channel(904684811225030656)
                        mbed = discord.Embed(
                            title=f"**{payload.member.name} HAS JOINED**",
                            description=f"*Ticket Number: {ticket_number}*")
                        #await channel.send(
                        #    f"@everyone; {payload.member.name} has joined ; *Ticket Number: {ticket_number}*, **Plz Type Your Problem Here**"
                        #)
                        await channel.send(embed=mbed)
                        #await msg.add_reaction("\ud83d\udcd5")
                        #with open("jsons/selfroles.json", "r") as f:
                        #  self_roles = json.load(f)
                        #self_roles[str(msg.id)] = {}
                        #self_roles[str(msg.id)]['emojis'] = emojis
                        #self_roles[str(msg.id)]['roles'] = roles
                        #self_roles[str(msg.id)]['work'] = "ticket_close"
                        #with open("jsons/selfroles.json", "w") as f:
                        #  json.dump(self_roles, f)
                elif self_roles[str(msg_id)]["work"] == "ticket_close":
                    with open("jsons/tickets_info.json", "r") as f:
                        data = json.load(f)
                    if str(payload.member.id) in data:
                        ticket_number = data[str(
                            payload.member.id)]['ticket_number']
                        del self_roles[str(msg_id)]
                        del data[str(payload.member.id)]
                        with open("jsons/tickets_info.json", "w") as f:
                            json.dump(data, f)
                        with open("jsons/selfroles.json", "w") as f:
                            json.dump(self_roles, f)
                        role = discord.utils.get(g.roles, name="Active-Ticket")
                        await payload.member.remove_roles(role)
                    else:
                        print("huh? :error:")
                elif self_roles[str(
                        msg_id)]["work"] == "minecraft_account_verification":
                    #bot_msg = await bot.fetch_message(msg_id)
                    userid = self_roles[str(msg_id)]['user']
                    user = bot.get_user(userid)
                    del self_roles[str(msg_id)]
                    with open("jsons/selfroles.json", "w") as f:
                        json.dump(self_roles, f)
                    await user.send(
                        "You're Now Whitelisted In The Server And You Can turn On The Server From Aternos"
                    )
                else:
                    await payload.member.add_roles(r)
                    await payload.member.send(
                        f"You Got **{selected_role}** Role!")


@bot.event
async def on_raw_reaction_remove(payload):
  if server_in_lockdown[0] == "in_lockdown":
    await payload.member.send("Server Is In Complete Lockdown Because Of Which You Won't Be Able to Use **Verfication, Self Roles, Requests, Tickets, And etc**")
  else:
    msg_id = payload.message_id

    with open("jsons/selfroles.json", "r") as f:
        self_roles = json.load(f)

    if str(msg_id) in self_roles:
        emojis = []
        roles = []

        for emoji in self_roles[str(msg_id)]["emojis"]:
            emojis.append(emoji)

        for role in self_roles[str(msg_id)]["roles"]:
            roles.append(role)

        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
        g = bot.get_guild(guild_id)

        print(emojis)
        print("choosed Emoji: ", payload.emoji)

        for i in range(len(emojis)):
            choosed_emoji = str(payload.emoji)
            if choosed_emoji == emojis[i]:
                selected_role = roles[i]

                r = discord.utils.get(g.roles, name=selected_role)

                member = await (g.fetch_member(payload.user_id))
                if member is not None:
                    await member.remove_roles(r)


@bot.event
async def on_member_join(member):
    #General.add_user_data(member)

    channel = bot.get_channel(875421282286592081)
    role = get(member.guild.roles, name="Non-Verified")
    await member.add_roles(role)
    await channel.send(
        f"Heya {member.mention}!" +
        " Welcome To **Syndicate* For More Information Go To <#875000973221838849>"
    )
    file = await General.make_welcome_card(member)
    await channel.send(file=file)
    await member.send(
        f"Welcome To **Syndicate*; To Get Full Access To The Server Get Verified at <#904019281249959957>"
    )


@bot.event
async def on_member_remove(member):
    General.remove_user_data(member)


################# DASHBOARD RELATED COMMANDS


@bot.command(name="check_for_embed")
@commands.has_role("Bot-Mod")
async def check_for_embed(ctx):
    data_raw = requests.get(
        "https://a.advic.repl.co/just_random_thing/requests")
    data = data_raw.text

    if str(data) == "NONE":
        await ctx.send("No Request For Embed Was Found")
    else:
        nan = requests.get(
            "https://a.advic.repl.co/just_random_thing/clear_request")
        await ctx.send("Embed request has been accepted sending embed", delete_after=10)

        data_splited = data.split("£")
        embed_title = data_splited[0]
        embed_message = data_splited[1]

        channel_id = data_splited[3]
        channel = bot.get_channel(int(channel_id))

        embed_color = data_splited[2].split(",")
        mbed = discord.Embed(title=embed_title,
                             description=embed_message,
                             color=discord.Color.from_rgb(
                                 int(embed_color[0]), int(embed_color[1]),
                                 int(embed_color[2])))

        await channel.send(embed=mbed)


keep_alive()
bot.run(token)


class Other_commands():
    async def send_embed_main(title, message, color, channel_id):
        try:
            mbed = discord.Embed(
                title=title,
                description=message,
                color=color,
            )
        except Exception as e:
            return f"{e} + + exit_code 0"
        try:
            channel = bot.get_channel(channel_id)
            await channel.send(embed=mbed)
        except Exception as e:
            return f"{e} + + exit_code 1"
        return "message_sent + + exit_code 2"
