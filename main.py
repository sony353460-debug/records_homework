import os
from dotenv import load_dotenv #用來讀取env檔裡的內容
import discord
from discord.commands import slash_command #斜線指令套件
from discord.commands import Option #選單套件
from discord import Embed
from database import recordDB
import datetime
from datetime import date
# import matplotlib.pyplot as plt

load_dotenv()

db=recordDB()

bot=discord.Bot(intents=discord.Intents.all())
#機器人啟動提示
@bot.event#定義事件
async def on_ready():#定義為On_ready
    print(f"{bot.user} IS ON")


#登入系統
@bot.slash_command(name="登入",description="輸入使用者密碼，初次使用則設定密碼")
async def login(ctx,password):
    user_id=str(ctx.author.id)
    user_data=db.get_user(user_id)
    if user_data==None:
        status=db.add_user(user_id,password)
        if status==True:
            await ctx.respond("成功新增帳戶")
        else:
            await ctx.respond("新增帳戶失敗")
    else:
        if user_data[0]==password:
            await ctx.respond("登入成功")
        else:
            await ctx.respond("密碼錯誤")

#新增消費功能
@bot.slash_command(name="新增",description="新增消費")
async def add_cost(ctx,item,amount,type: Option(str, "選擇收支類型", choices=["收入", "支出"])):#我也不知道為甚麼會有黃色波浪號，但能跑就行
    await ctx.defer()   # 🔥 告訴 Discord：我在處理中
    user_id = str(ctx.author.id)
    today = datetime.date.today()
    db.add_record(user_id,today,item,amount,type)
    await ctx.respond("成功記入帳本")
#查詢帳本功能
@bot.slash_command(name="查詢",description="查詢帳本")
async def search_records(ctx):
    user_id=str(ctx.author.id)
    rows=db.search_records(user_id)
    # 表頭
    embed = Embed(title="📒 記帳紀錄")

    for r in rows:
        id, user_id, today, item, amount, category = r
        embed.add_field(
            name=f"ID: {id}",
            value=f"📅 {today}\n📌 {item}\n💵 {amount}\n🔖 {category}",
            inline=False
        )
    await ctx.respond(embed=embed)   # 用 code block 固定寬度

#修改帳本功能
@bot.slash_command(name="修改",description="修改帳本")
async def edit_record(ctx,id,item,amount):
    user_id=str(ctx.author.id)
    db.edit_record(id,user_id,item,amount)
    await ctx.respond(f"已修改第{id}筆記錄")
#生成消費分析圖表

bot.run(os.environ.get("DISCORD_TOKEN"))











# #機器人(練習)
# @bot.event
# async def on_message(message):#定義
#     if message.author==bot.user:#偵測到的訊息來源等於機器人本身則跳出，避免bug
#         return
#     if message.content=="hellow":#偵測訊息內容是否符合
#         await message.channel.send("hi")
#     if message.content.startswith("測試"):#偵測內容開頭是否符合
#         await message.channel.send("測試成功")
# #機器人(練習)
# @bot.event
# async def on_member_join(member):
#     channel_id=1442521104315846838
#     welcome_channel=bot.get(channel_id)
#     await welcome_channel.send(f"歡迎{member.mention}加入伺服器")