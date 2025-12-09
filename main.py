import os
from dotenv import load_dotenv #用來讀取env檔裡的內容
#discord套件
import discord
from discord.commands import slash_command #斜線指令套件
from discord.commands import Option #選單套件
from discord import Embed
from discord.ui import View #這邊只用到View
#將我寫的其他檔案導入
from database import recordDB #資料庫程式
from modals import add_record_modal #選單的各項功能(正在做)
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
    #處理 View 註冊和重複添加檢查
    bot.add_view(menu(user_id=None))


#登入系統
@bot.slash_command(name="登入",description="輸入使用者密碼，初次使用則設定密碼")
async def login(ctx,password):

    await ctx.defer(ephemeral=False)

    user_id=str(ctx.author.id)
    user_data=db.get_user(user_id)

    print(logged_in_users)

    if logged_in_users.get(user_id)==True:
        await ctx.followup.send("已登入，按下按鈕選擇功能",view=menu(user_id),ephemeral=False)
        return
    else:
        print(logged_in_users)
        if user_data==None:
            status=db.add_user(user_id,password)
            if status==True:
                logged_in_users[user_id]=True
                await ctx.followup.send("成功新增帳戶",view=menu(user_id),ephemeral=False)
                return
            else:
                await ctx.followup.send("新增帳戶失敗",ephemeral=True)
                return
        else:
            if user_data[0]==password:
                logged_in_users[user_id]=True
                print(logged_in_users)
                await ctx.followup.send("登入成功",view=menu(user_id),ephemeral=False)
                return
            else:
                await ctx.followup.send("密碼錯誤",ephemeral=True)
                return

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
        print("checkpoint")
        # 🎯 檢查操作者是否為本人
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("你不能操作別人的選單。", ephemeral=True)
            return
        #判斷按下的是哪個按鈕，以進入該功能
        if custom_id=="action_add":
            await interaction.response.send_modal(add_record_modal(parent_view=self))
        elif custom_id=="action_search":
            await interaction.response.send_modal(search_records_modal(title="查詢記帳記錄", parent_view=self))
        elif custom_id=="action_edit":
            await interaction.response.send_modal(edit_record_modal(title="修改記帳記錄", parent_view=self))
        elif custom_id=="action_delete":
            await interaction.response.send_modal(delete_record_modal(title="刪除記帳記錄", parent_view=self))
        elif custom_id=="action_analyze":
            await interaction.response.send_message("圖表分析功能即將推出...", ephemeral=True)
        elif custom_id=="action_signout":
            logged_in_users[self.user_id]=False
            await interaction.response.edit_message(content="**✅ 成功登出！** 請使用 `/登入` 再次操作。", view=None)

'''
# 🎯 新增 Modal (AddRecordModal)
class AddRecordModal(Modal):
    def __init__(self, parent_view, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.parent_view = parent_view 
        self.add_item(InputText(label="項目名稱", placeholder="例如：晚餐、薪水"))
        self.add_item(InputText(label="金額 (數字)", placeholder="例如：500、-200"))
        self.add_item(InputText(label="類型 (收入/支出)", placeholder="輸入 收入 或 支出"))

    async def callback(self, interaction: discord.Interaction):
        item = self.children[0].value
        amount_str = self.children[1].value
        record_type = self.children[2].value
        user_id = self.parent_view.user_id # 從 View 獲取 user_id

        try:
            amount = int(amount_str)
        except ValueError:
            await interaction.response.send_message("金額必須是數字。", ephemeral=True)
            return
        
        if record_type not in ["收入", "支出"]:
            await interaction.response.send_message("類型必須是 '收入' 或 '支出'。", ephemeral=True)
            return

        today = datetime.date.today()
        db.add_record(user_id, today, item, amount, record_type)
        
        await interaction.response.send_message(f"✅ 成功新增紀錄：{record_type} {item}，金額 {amount}。", ephemeral=True)

# 🎯 新增 Modal (EditRecordModal)
class EditRecordModal(Modal):
    def __init__(self, parent_view, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.parent_view = parent_view
        self.add_item(InputText(label="記錄 ID", placeholder="輸入要修改的記錄 ID"))
        self.add_item(InputText(label="新項目名稱", placeholder="例如：新的咖啡"))
        self.add_item(InputText(label="新金額 (數字)", placeholder="例如：-100"))

    async def callback(self, interaction: discord.Interaction):
        record_id_str = self.children[0].value
        item = self.children[1].value
        amount_str = self.children[2].value
        user_id = self.parent_view.user_id

        try:
            record_id = int(record_id_str)
            amount = int(amount_str)
        except ValueError:
            await interaction.response.send_message("ID 和金額必須是數字。", ephemeral=True)
            return

        db.edit_record(record_id, user_id, item, amount) 
        
        await interaction.response.send_message(f"✅ 已嘗試修改 ID {record_id} 的記錄為：{item}, {amount}。", ephemeral=True)

# 🎯 新增 Modal (DeleteRecordModal)
class DeleteRecordModal(Modal):
    def __init__(self, parent_view, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.parent_view = parent_view
        self.add_item(InputText(label="記錄 ID", placeholder="輸入要刪除的記錄 ID"))

    async def callback(self, interaction: discord.Interaction):
        record_id_str = self.children[0].value
        user_id = self.parent_view.user_id
        
        try:
            record_id = int(record_id_str)
        except ValueError:
            await interaction.response.send_message("ID 必須是數字。", ephemeral=True)
            return

        # 🎯 確保 db.delete_record 接受兩個參數 (id, user_id) 進行驗證
        db.delete_record(record_id, user_id) 
        
        await interaction.response.send_message(f"✅ 已嘗試刪除 ID {record_id} 的記錄。", ephemeral=True)
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