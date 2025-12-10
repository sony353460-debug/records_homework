import os
from dotenv import load_dotenv #用來讀取env檔裡的內容
#discord套件
import discord
from discord.commands import slash_command #斜線指令套件
from discord.commands import Option #選單套件
from discord import Embed
from discord.ui import View,Button 
#將我寫的其他檔案導入
from database import recordDB #資料庫程式
from modals import add_record_modal ,search_records_embed ,edit_record_modal ,delete_record_modal ,profile_embed#選單的各項功能(正在做)
import datetime
from datetime import date
# import matplotlib.pyplot as plt

logged_in_users = {}#紀錄已登入的使用者
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

    print(logged_in_users)

    if logged_in_users.get(user_id)==True:
        message="已登入，按下按鈕選擇功能"
    else:
        if user_data==None:
            status=db.add_user(user_id,password)
            if status==True:
                logged_in_users[user_id]=True
                message="成功新增帳戶"
            else:
                await ctx.respond("新增帳戶失敗",ephemeral=True)
                return
        else:
            if user_data[0]==password:
                logged_in_users[user_id]=True
                message="登入成功"
            else:
                await ctx.respond("密碼錯誤",ephemeral=True)
                return
    await ctx.respond(message,view=menu(user_id),ephemeral=False)         
    


class menu(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = str(user_id)

    async def interaction_check(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("你不能操作別人的選單。", ephemeral=True)
            return False
        return True

    # ---------------- Buttons ----------------
    @discord.ui.button(label="新增紀錄", emoji="📥", custom_id="action_add", style=discord.ButtonStyle.green, row=0)
    async def add_record(self, button, interaction):
        await interaction.response.send_modal(add_record_modal(parent_view=self))
        
    @discord.ui.button(label="查詢紀錄", emoji="🔍", custom_id="action_search", style=discord.ButtonStyle.grey, row=0)
    async def search_record(self, button, interaction):
        embed = search_records_embed(parent_view=self).get_embed()
        await interaction.response.edit_message(content="查詢紀錄",embed=embed,view=BackView(self))

    @discord.ui.button(label="修改紀錄", emoji="✏️", custom_id="action_edit", style=discord.ButtonStyle.blurple, row=0)
    async def edit_record(self, button, interaction):
        await interaction.response.send_modal(edit_record_modal(parent_view=self))

    @discord.ui.button(label="刪除紀錄", emoji="🗑️", custom_id="action_delete", style=discord.ButtonStyle.red, row=0)
    async def delete_record(self, button, interaction):
        await interaction.response.send_modal(delete_record_modal(parent_view=self))

    @discord.ui.button(label="個人資料", emoji="🪪", custom_id="action_profile", style=discord.ButtonStyle.green, row=1)
    async def profile(self, button, interaction):
        embed = profile_embed(parent_view=self).get_embed()
        await interaction.response.edit_message(content="個人資料",embed=embed,view=BackView(self))

    @discord.ui.button(label="圖表分析", emoji="📊", custom_id="action_analyze", style=discord.ButtonStyle.grey, row=1)
    async def analyze(self, button, interaction):
        await interaction.response.send_message(content="圖表分析功能即將推出...",view=BackView(self))

    @discord.ui.button(label="修改個資", emoji="🔐", custom_id="action_password", style=discord.ButtonStyle.blurple, row=1)
    async def password(self, button, interaction):
        await interaction.response.send_message(content="修改個資",view=BackView(self))

    @discord.ui.button(label="登出系統", emoji="🚪", custom_id="action_signout", style=discord.ButtonStyle.red, row=1)
    async def logout(self, button, interaction):
        logged_in_users[self.user_id] = False
        await interaction.response.edit_message(content="已登出", view=None)

    

#返回選單的按鈕
class BackView(discord.ui.View):
    def __init__(self, parent_view: discord.ui.View):
        super().__init__(timeout=180)
        print(parent_view)
        self.parent_view = parent_view
        
    @discord.ui.button(label="返回主選單", style=discord.ButtonStyle.primary)
    async def back(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="主選單：",embed=None,view=self.parent_view)       # ← 回到原本選單




'''
#登入後的選單
class menu(discord.ui.View):
    def __init__(self,user_id=None):
        super().__init__(timeout=None)
        self.user_id=user_id if user_id is not None else None

        self.custom_id = menu.__qualname__

        #self.add_item是產生按鈕的語法
        self.add_item(discord.ui.Button(label="新增紀錄",custom_id="action_add",style=discord.ButtonStyle.green,row=0))
        self.add_item(discord.ui.Button(label="查詢紀錄",custom_id="action_search",style=discord.ButtonStyle.grey,row=0))
        self.add_item(discord.ui.Button(label="修改紀錄",custom_id="action_edit",style=discord.ButtonStyle.blurple,row=0))
        self.add_item(discord.ui.Button(label="刪除紀錄",custom_id="action_delete",style=discord.ButtonStyle.red,row=1))
        self.add_item(discord.ui.Button(label="圖表分析",custom_id="action_analyze",style=discord.ButtonStyle.green,row=1))
        self.add_item(discord.ui.Button(label="登出系統",custom_id="action_signout",style=discord.ButtonStyle.green,row=1))
        
            
    #當按鈕被按下
    async def interaction_check(self,interaction:discord.Interaction):
        custom_id=interaction.data["custom_id"]
        print(logged_in_users)
        print(str(interaction.user.id),self.user_id)
        # 🎯 檢查操作者是否為本人
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("你不能操作別人的選單。", ephemeral=True)
            return
        #判斷按下的是哪個按鈕，以進入該功能
        if custom_id=="action_add":
            await interaction.response.send_modal(add_record_modal(parent_view=self))
        elif custom_id=="action_search":
            embed=search_records_embed(parent_view=self).get_embed()
            await interaction.response.send_message(content="查詢結果：",embed=embed,view=BackView(parent_view=self),ephemeral=False)  # ← 清除原本按鈕，提供返回鍵
        elif custom_id=="action_edit":
            await interaction.response.send_modal(edit_record_modal(parent_view=self))
        elif custom_id=="action_delete":
            await interaction.followup.send(delete_record_modal(title="刪除記帳記錄", parent_view=self))
        elif custom_id=="action_analyze":
            await interaction.followup.send("圖表分析功能即將推出...", ephemeral=True)
        elif custom_id=="action_signout":
            logged_in_users[self.user_id]=False
            await interaction.followup.edit_message(content="**✅ 成功登出！** 請使用 `/登入` 再次操作。", view=None)

#返回選單的按鈕
class BackView(discord.ui.View):
    def __init__(self, parent_view: discord.ui.View):
        super().__init__(timeout=None)
        self.parent_view = parent_view

    @discord.ui.button(label="返回主選單", style=discord.ButtonStyle.primary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="主選單：",view=self.parent_view)       # ← 回到原本選單
'''

bot.run(os.environ.get("DISCORD_TOKEN"))




















# #新增消費功能
# @bot.slash_command(name="新增",description="新增消費")
# async def add_cost(ctx,item,amount,type: Option(str, "選擇收支類型", choices=["收入", "支出"])):#我也不知道為甚麼會有黃色波浪號，但能跑就行
#     await ctx.defer()   # 🔥 告訴 Discord：我在處理中
#     user_id = str(ctx.author.id)
#     today = datetime.date.today()
#     db.add_record(user_id,today,item,amount,type)
#     await ctx.respond("成功記入帳本")

# #查詢帳本功能
# @bot.slash_command(name="查詢",description="查詢帳本")
# async def search_records(ctx):
#     user_id=str(ctx.author.id)
#     rows=db.search_records(user_id)
#     # 表頭
#     embed = Embed(title="📒 記帳紀錄")

#     for r in rows:
#         id, user_id, today, item, amount, category = r
#         embed.add_field(
#             name=f"ID: {id}",
#             value=f"📅 {today}\n📌 {item}\n💵 {amount}\n🔖 {category}",
#             inline=False
#         )
#     await ctx.respond(embed=embed)   # 用 code block 固定寬度

# #修改帳本功能
# @bot.slash_command(name="修改",description="修改帳本")
# async def edit_record(ctx,id,item,amount):
#     user_id=str(ctx.author.id)
#     db.edit_record(id,user_id,item,amount)
#     await ctx.respond(f"已修改第{id}筆記錄")

# #生成消費分析圖表







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