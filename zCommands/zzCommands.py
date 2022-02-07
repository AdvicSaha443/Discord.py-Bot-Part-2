import os
import json
import random

from discord import File
from pymongo import MongoClient
from datetime import datetime, timedelta
from easy_pil import Editor, Canvas, load_image_async, Font

level = ['Level-5+', 'Level-10+', 'Level-15+', 'Level-20+', 'Level-25+', 'Level-30+', 'Level-40+', 'Level-50+', 'Level-75+', 'Level-100+', 'Level-150+']
levelnum = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150]

my_secret = os.environ['clusterr']
cluster = MongoClient(my_secret)

lvls_db = cluster["DiscordBot"]["Levelling"]

class Levels():
  def increase_xp(userid: str, guildid: str, increaseby: int):
    lvls_db_user = lvls_db.find_one({"id":userid})

    if lvls_db_user is None:     
      newuser = {"id":userid, "lvl":1, "xp":0}
      lvls_db.insert_one(newuser)
    else:
      xp = lvls_db_user["xp"]
      new_xp = increaseby+xp
      lvls_db.update_one({"id":userid}, {"$set":{"xp":new_xp}})
      new_level = int((xp+increaseby)/100)
      
      lvl = lvls_db_user["lvl"]
      send_data = "NONE"  

      if new_level > lvl:
        lvls_db.update_one({"id":userid}, {"$set":{"lvl":new_level}})
        lvls_db.update_one({"id":userid}, {"$set":{"xp":0}})
        for i in range(len(level)):
          if new_level == levelnum[i]:
            send_data = f"NEW-LEVEL-ROLES {new_level} {level[i]}"
            break
          else:
            send_data = f"NEW-LEVEL {new_level}"

      return send_data

  def get_rank_info(userid: str):
    lvls_db_user = lvls_db.find_one({"id":str(userid)})

    if lvls_db_user is None:     
      newuser = {"id":userid, "lvl":1, "xp":0}
      lvls_db.insert_one(newuser)
      return "newuser"
    else:
      xp = int(lvls_db_user["xp"])
      level = int(lvls_db_user["lvl"])
      xp_for_next_level = int((level+1)*100)
      xp_need = int(xp_for_next_level-xp)
      percent_done=int((xp/xp_for_next_level)*100)
      message_more_needed = round(xp_need/20)

      data = {
        "xp": xp,
        "level": level,
        "xp_for_next_level": xp_for_next_level,
        "xp_need": xp_need,
        "percent_done": percent_done,
        "message_more_needed": message_more_needed
      }
      return data

  def decrease_xp(userid: str, guildid: str, mode: str, decreaseby: int):
    with open("jsons/levels.json", "r") as f:
      data = json.load(f)
    data[guildid][userid][mode] =- decreaseby
    with open("jsons/levels.json", "w") as f:
      json.dump(data, f)
  
  def get_user_details(guildid: str, userid: str):
    with open("jsons/levels.json", "r") as f:
      data = json.load(f)
    try:
      user = data[guildid][userid]
      return user
    except:
      return None

  def add_user_all_guild_data(user):
    with open("jsons/userdata.json", "r") as f:
        data = json.load(f)
    if str(user.id) in data:
      return
    data[str(user.id)] = {}
    data[str(user.id)]['card'] = 0
    data[str(user.id)]['text'] = "#fff"
    data[str(user.id)]['bar'] = "#17F3F6"
    data[str(user.id)]['blend'] = 0
    with open("jsons/userdata.json", "w") as f:
      json.dump(data, f)

  async def make_user_rank_card(guildid: str, userid: str, avatarurl: str, username: str):
    lvls_db_user = lvls_db.find_one({"id":str(userid)})

    if lvls_db_user is None:
      return 0
    
    with open("jsons/userdata.json", "r") as f:
      user_data = json.load(f)
    
    xp = lvls_db_user["xp"]
    lvl = lvls_db_user["lvl"]
    image = user_data[str(userid)]['card']

    next_level_xp = (lvl+1) * 100
    current_level_xp = lvl * 100
    xp_need = next_level_xp
    xp_have = lvls_db_user["xp"]

    percentage = int(((xp_have * 100)/ xp_need))

    if percentage < 1:
      percentage = 0
    
    ## Rank card
    background = Editor(f"images/{image}.png")
    profile = await load_image_async(str(avatarurl))

    profile = Editor(profile).resize((150, 150)).circle_image()

    poppins = Font().poppins(size=40)
    poppins_small = Font().poppins(size=30)

    co = (0, 0, 0)
    TRANSPARENCY = 25  # Degree of transparency, 0-100%
    OPACITY = int(255 * TRANSPARENCY)
    ima = Editor("images/anothertry.png")
    
    if user_data[str(userid)]['blend'] == 1:
      background.blend(image=ima, alpha=.5, on_top=False)

    #background.paste(square.image, (600, -250))
    background.paste(profile.image, (30, 30))

    background.rectangle((30, 220), width=650, height=40, fill="#fff", radius=20)
    background.bar(
        (30, 220),
        max_width=650,
        height=40,
        percentage=percentage,
        fill=user_data[str(userid)]['bar'],
        radius=20,
    )
    background.text((200, 40), str(username), font=poppins, color=user_data[str(userid)]['text'])

    background.rectangle((200, 100), width=350, height=2, fill=user_data[str(userid)]['bar'])
    background.text(
        (200, 130),
        f"Level : {lvl}   "
        + f" XP : {xp} / {(lvl+1) * 100}",
        font=poppins_small,
        color=user_data[str(userid)]['text'],
    )

    file = File(fp=background.image_bytes, filename="images/card.png")
    return file
  
  async def make_user_rank_card_just_for_showing_them_lol(userid: str, avatar_url: str, user_name: str):
    with open("jsons/userdata.json", "r") as f:
        user_data = json.load(f)
    xp = 3250
    lvl = 78
    image = user_data[str(userid)]['card']

    next_level_xp = (lvl+1) * 100
    current_level_xp = lvl * 100
    xp_need = next_level_xp
    xp_have = 3250

    percentage = int(((xp_have * 100)/ xp_need))

    if percentage < 1:
      percentage = 0
    
    ## Rank card
    background = Editor(f"images/{image}.png")
    profile = await load_image_async(str(avatar_url))

    profile = Editor(profile).resize((150, 150)).circle_image()

    poppins = Font().poppins(size=40)
    poppins_small = Font().poppins(size=30)

    co = (0, 0, 0)
    TRANSPARENCY = 25  # Degree of transparency, 0-100%
    OPACITY = int(255 * TRANSPARENCY)
    ima = Editor("images/anothertry.png")
    
    if user_data[str(userid)]['blend'] == 1:
      background.blend(image=ima, alpha=.5, on_top=False)

    #background.paste(square.image, (600, -250))
    background.paste(profile.image, (30, 30))

    background.rectangle((30, 220), width=650, height=40, fill="#fff", radius=20)
    background.bar(
        (30, 220),
        max_width=650,
        height=40,
        percentage=percentage,
        fill=user_data[str(userid)]['bar'],
        radius=20,
    )
    background.text((200, 40), str(user_name), font=poppins, color=user_data[str(userid)]['text'])

    background.rectangle((200, 100), width=350, height=2, fill=user_data[str(userid)]['bar'])
    background.text(
        (200, 130),
        f"Level : {lvl}   "
        + f" XP : {xp} / {(lvl+1) * 100}",
        font=poppins_small,
        color=user_data[str(userid)]['text'],
    )

    file = File(fp=background.image_bytes, filename="images/card.png")
    return file

class Economy():
  def increase_money(userid: str, guildid: str):
    with open("jsons/mainBank.json", "r") as f:
      data = json.load(f)
    if str(guildid) in data:
      try:
        if data[str(userid)] is not None:
          if data[str(userid)]['sb'] == 1:
            data[str(userid)]['bank'] += 1200
            data[str(guildid)]['bank'] += 600
          else:
            data[str(userid)]['bank'] += 700
            data[str(guildid)]['bank'] += 300
          
          with open("jsons/mainBank.json", "w") as f:
            json.dump(data, f)
      except:
        data[str(userid)] = {}
        data[str(userid)]['wallet'] = 0
        data[str(userid)]['bank'] = 100
        data[str(userid)]['hide'] = 0
        data[str(userid)]['sb'] = 0
        data[str(userid)]['type'] = "user"

        with open("jsons/mainBank.json", "w") as f:
          json.dump(data, f)
    else:
      data[str(guildid)] = {}
      data[str(guildid)]['bank'] = 100
      data[str(guildid)]['type'] = "guild"

      with open("jsons/mainBank.json", "w") as f:
        json.dump(data, f)

  def get_bank_data():
    with open("jsons/mainBank.json", "r") as f:
      data = json.load(f)
    return data

  def decrease_user_money(change, userid, guilid):
    data = Economy.get_bank_data()
    
    data[str(userid)]["bank"]+=(-1*change)
    data[str(guilid)]["bank"]+=change

    with open("jsons/mainBank.json", "w") as f:
      json.dump(data, f)

  def update_bank(user, change = 0, mode="wallet"):
    users = Economy.get_bank_data()

    users[str(user.id)][mode] +=change

    with open("jsons/mainBank.json", "w") as f:
      json.dump(users, f)
    
    bal = [users[str(user.id)]['wallet'],users[str(user.id)]['bank']]

    return bal
  
  def update_bank_using_id(userid: str, change = 0, mode="wallet"):
    users = Economy.get_bank_data()

    users[str(userid)][mode] +=change

    with open("jsons/mainBank.json", "w") as f:
      json.dump(users, f)

  def open_account(user): 
    users = Economy.get_bank_data()
    
    if str(user.id) in users:
      return False
    else:
      users[str(user.id)] = {}
      users[str(user.id)]['wallet'] = 0
      users[str(user.id)]['bank'] = 100
      users[str(user.id)]['hide'] = 0
      users[str(user.id)]['sb'] = 0
      users[str(user.id)]['type'] = "user"

    with open("jsons/mainBank.json", "w") as f:
      json.dump(users, f)
    
    return True
  
  def decrease_money(userid: str, decreaseby: int):
    with open("jsons/mainBank.json", "r") as f:
      users = json.load(f)
    users[str(userid)]['bank'] -= decreaseby
    with open("jsons/mainBank.json", "w") as f:
      json.dump(users, f)

class General():
  async def make_welcome_card(member):
    pos = sum(m.joined_at < member.joined_at for m in member.guild.members if m.joined_at is not None)
    if pos == 1:
      te = "st"
    elif pos == 2:
      te = "nd"
    elif pos == 3:
      te = "rd"
    else:
      te = "th"

    background = Editor("jsons/wlcbg.jpg")
    profile_image = await load_image_async(str(member.avatar_url))

    profile = Editor(profile_image).resize((150, 150)).circle_image()
    poppins = Font().poppins(size=50, variant="bold")

    poppins_small = Font().poppins(size=25, variant="regular")
    poppins_light = Font().poppins(size=20, variant="light")

    background.paste(profile, (325, 90))
    background.ellipse((325, 90), 150, 150, outline="gold", stroke_width=4)

    #guildname = member.guild.name
    background.text((400, 260), "WELCOME TO SYNDICATE", color="white", font=poppins, align="center")

    background.text(
        (400, 325), f"{member.name}#{member.discriminator}", color="white", font=poppins_small, align="center"
    )

    background.text(
        (400, 360),
        f"You are the {pos}{te} Member",
        color="#0BE7F5",
        font=poppins_small,
        align="center",
    )

    file = File(fp=background.image_bytes, filename="jsons/wlcbg.jpg")
    return file

  def add_user_data(user):
    def add_levels():
      with open("jsons/levels.json", "r") as f:
        data = json.load(f)
      if str(user.id) in data[str(user.guild.id)]:
        return
      data[str(user.guild.id)][str(user.id)] = {}
      data[str(user.guild.id)][str(user.id)]['xp'] = 0
      data[str(user.guild.id)][str(user.id)]['level'] = 1
      data[str(user.guild.id)][str(user.id)]['card'] = 0
      data[str(user.guild.id)][str(user.id)]['text'] = "#fff"
      data[str(user.guild.id)][str(user.id)]['bar'] = "#17F3F6"
      data[str(user.guild.id)][str(user.id)]['blend'] = 0
      with open("jsons/levels.json", "w") as f:
        json.dump(data, f)
    
    def add_user_data():
      with open("jsons/userdata.json", "r") as f:
        data = json.load(f)
      data[str(user.id)] = {}
      data[str(user.id)]['card'] = 0
      data[str(user.id)]['text'] = "#fff"
      data[str(user.id)]['bar'] = "#17F3F6"
      data[str(user.id)]['blend'] = 0
      with open("jsons/userdata.json", "w") as f:
        json.dump(data, f)

    def add_mute_data():
      with open("jsons/muted.json", "r") as f:
        data2 = json.load(f)
      if data2 is not None:
        try:
          if str(user.id) in data2[str(user.guild.id)]:
            return
          data2[str(user.guild.id)][str(user.id)]['muted'] = 0
          data2[str(user.guild.id)][str(user.id)]['muted_on'] = 0
          data2[str(user.guild.id)][str(user.id)]['unmute_at'] = 0

          with open("jsons/muted.json", "w") as f:
            json.dump(data2, f)
        except:
          pass
      
    
    def open_account():
      Economy.open_account(user)

    add_levels()
    open_account()
    #add_mute_data()

  def list_to_string(s): 
    str1 = "" 
    for ele in s: 
        str1 += ele  
    return str1 

  def make_new_ticket(user_id):
    with open("jsons/tickets_info.json", "r") as f:
      data = json.load(f)
    if str(user_id) in data:
      return "0"
    else:
      ticket_number = f"ticket#{random.randint(1000,9999)}"
      for user in data:
        if ticket_number in data[str(user)]["ticket_number"]:
          ticket_number = f"ticket#{random.randint(1000,9999)}"
          break
      data[str(user_id)] = {}
      data[str(user_id)]["ticket_number"] = ticket_number
      with open("jsons/tickets_info.json", "w") as f:
        json.dump(data, f)
      return ticket_number

  def remove_user_data(user):
    def delete_levels():
      with open("jsons/levels.json", "r") as f:
        data1 = json.load(f)
      del data1[str(user.guild.id)][str(user.id)]
      with open("jsons/levels.json", "w") as f:
        json.dump(data1, f)
      
    def delete_account():
      with open("jsons/mainBank.json", "r") as f:
        data2 = json.load(f)
      del data2[str(user.id)]
      with open("jsons/mainBank.json", "w") as f:
        json.dump(data2, f)

    def delete_mute_data():
      with open("jsons/muted.json", "r") as f:
        data3 = json.load(f)
      del data3[str(user.guild.id)][str(user.id)]
      with open("jsons/muted.json", "r") as f:
        json.dump(data3, f)

    delete_levels()
    #delete_account()
    #delete_mute_data()

class Auto_Moderation():
  def mute(guildid: str, userid: str, curtime: str, unmuteafter: int):
    with open("jsons/muted.json", "r") as f:
      data = json.load(f)
    unmute_at = Time.add_time(curtime, unmuteafter)
    try:
      if data[str(guildid)] is not None:
        try:
          if data[str(guildid)][str(userid)] is not None:
            if data[str(guildid)][str(userid)]['muted'] == 0:
              data[str(guildid)][str(userid)]['muted'] = 1
              data[str(guildid)][str(userid)]['muted_on'] = curtime
              data[str(guildid)][str(userid)]['unmute_at'] = unmute_at

              with open("jsons/muted.json", "w") as f:
                json.dump(data, f)

              return "DONE"
            else:
              return "ALREADY_MUTED"
        except:
          data[str(guildid)][str(userid)] = {}
          data[str(guildid)][str(userid)]['muted'] = 1
          data[str(guildid)][str(userid)]['muted_on'] = curtime
          data[str(guildid)][str(userid)]['unmute_at'] = unmute_at
          with open("jsons/muted.json", "w") as f:
            json.dump(data, f)
          return "DONE"
    except:
      data[str(guildid)] = {}
      data[str(guildid)][str(userid)] = {}
      data[str(guildid)][str(userid)]['muted'] = 1
      data[str(guildid)][str(userid)]['muted_on'] = curtime
      data[str(guildid)][str(userid)]['unmute_at'] = unmute_at
      with open("jsons/muted.json", "w") as f:
        json.dump(data, f)
      return "DONE"


class Time():
  def convert_time(num: int, mode: str):
    if mode == "s":
      return num
    elif mode == "m":
      return num*60
    elif mode == "hr":
      return num*60*60
    else:
      return None
  
  def convert_time_direct(time):
    pos=["s", "m", "h", "d"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600*24}
    unit=time[-1]
    if unit not in pos:
      return -1
    try:
      val=int(time[:-1])
    except:
      return -2
    return val*time_dict[unit]

  def get_current_time(mode: str):
    if mode == "NORMAL":
      return datetime.utcnow()
    elif mode == "DATE":
      return datetime.utcnow().strftime("%d")
    elif mode == "HOUR":
      return datetime.utcnow().strftime("%H")
    elif mode == "MIN":
      return datetime.utcnow().strftime("%M")
    elif mode == "DHM":
      date = datetime.utcnow().strftime("%d")
      hour = datetime.utcnow().strftime("%H")
      min = datetime.utcnow().strftime("%M")
      min = datetime.utcnow().strftime("%M")
      data = date, " ", hour, " ", min
      return data

  def add_time(now: str, addTime: int):
    new_time = now+timedelta(seconds=addTime)
    return new_time

  def month(num: int):
    if num == 1:
      m = "January"
    elif num == 2:
      m = "February"
    elif num == 3:
      m = "March"
    elif num == 4:
      m = "April"
    elif num == 5:
      m = "May"
    elif num == 6:
      m = "June"
    elif num == 7:
      m = "July"
    elif num == 8:
      m = "August"
    elif num == 9:
      m = "September"
    elif num == 10:
      m = "October"
    elif num == 11:
      m = "November"
    elif num == 12:
      m = "December"
    return m

  def day(num: int):
    if num == 1:
      e = "st"
    elif num == 2:
      e = "nd"
    elif num == 3:
      e = "rd"
    else:
      e = "th"
    return e

  


#date = datetime.utcnow().strftime("%d")
#hour = datetime.utcnow().strftime("%H")
#min = datetime.utcnow().strftime("%M")


class Dashboard():
  def generate_new_key(lenght):
    letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', 'O', 'P', 'O', 'T', 'B', 'O', 'Q', 'W', 'E', 'R', 'Y', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    key_array = []
    for i in range(lenght):
      letter = random.choice(letters)
      key_array.append(letter)
    def listToString(s): 
      str1 = "" 
      for ele in s: 
          str1 += ele  
      return str1
    key = listToString(key_array)
    return key
  
  def add_code_data(giftcode, value):
    with open("jsons/gift_cards.txt", "r+") as f:
      f.write(f"{giftcode}-{value}\n")

  def zzmakeKey(no: int):
    temp_key_list = []
    for i in range(0, no):
      key = Dashboard.generate_new_key()
      temp_key_list.append(key)
    return temp_key_list

  def decode_reward_code(code: str):
    letter_type = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
    data = {"q": 1, "w": 2, "e": 3, "r": 4, "t": 5, "y": 6, "u": 7, "i": 8, "o": 9, "p": 0}
    temp_list = []
    for letter in code:
      if letter in letter_type:
        num = data.get(letter)
        temp_list.append(num)

    value = ''.join([str(elem) for elem in temp_list])
    return value

  def change_to_code(value: str):
    data = {"1": "q", "2": "w", "3": "e", "4": "r", "5": "t", "6": "y", "7": "u", "8": "i", "9": "o", "0": "p"}
    temp_list = []

    for num in value:
      data_num = data.get(num)
      temp_list.append(data_num)

    code = General.list_to_string(temp_list)
    return code

  async def send_embed(title: str, message: str, color: str, channel_id: int):
    #response = send_embed_main(title, message, color, channel_id)
    #return response
    return