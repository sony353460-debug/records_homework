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
from function import add_record_modal,search_records_embed,edit_record_modal,delete_record_modal,profile_embed,chart_analysis,target_modal#選單的各項功能(正在做)
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
        embed=search_records_embed(parent_view=self).get_embed()
        await interaction.response.edit_message(content="查詢紀錄",embed=embed,view=BackView(self))

    @discord.ui.button(label="修改紀錄", emoji="✏️", custom_id="action_edit", style=discord.ButtonStyle.blurple, row=0)
    async def edit_record(self, button, interaction):
        await interaction.response.send_modal(edit_record_modal(parent_view=self))

    @discord.ui.button(label="刪除紀錄", emoji="🗑️", custom_id="action_delete", style=discord.ButtonStyle.red, row=0)
    async def delete_record(self, button, interaction):
        await interaction.response.send_modal(delete_record_modal(parent_view=self))

    @discord.ui.button(label="個人資料", emoji="🪪", custom_id="action_profile", style=discord.ButtonStyle.green, row=1)
    async def profile(self, button, interaction):
        embed=profile_embed(parent_view=self).get_embed()
        await interaction.response.edit_message(content="個人資料",embed=embed,view=BackView(self))

    @discord.ui.button(label="圖表分析", emoji="📊", custom_id="chart_analysis", style=discord.ButtonStyle.grey, row=1)
    async def analyze(self, button, interaction):
        file_income,embed_income,file_expense,embed_expense,embed_advice=chart_analysis(parent_view=self).creat_chart()
        await interaction.response.defer()
        await interaction.edit_original_message(content="圖表分析",files=[file_income,file_expense],embeds=[embed_advice,embed_income,embed_expense],view=BackView(self))

    @discord.ui.button(label="目標預算", emoji="🎯", custom_id="action_target", style=discord.ButtonStyle.blurple, row=1)
    async def password(self, button, interaction):
        await interaction.response.send_modal(target_modal(parent_view=self))

    # @discord.ui.button(label="修改個資", emoji="🔐", custom_id="action_password", style=discord.ButtonStyle.blurple, row=1)
    # async def password(self, button, interaction):
    #     await interaction.response.send_message(content="修改個資",view=BackView(self))

    @discord.ui.button(label="登出系統", emoji="🚪", custom_id="action_signout", style=discord.ButtonStyle.red, row=1)
    async def logout(self, button, interaction):
        logged_in_users[self.user_id] = False
        await interaction.response.edit_message(content="已登出", view=None)

    

#返回選單的按鈕
class BackView(discord.ui.View):
    def __init__(self, parent_view: discord.ui.View):
        super().__init__(timeout=180)
        self.parent_view = parent_view
        
    @discord.ui.button(label="返回主選單", style=discord.ButtonStyle.primary)
    async def back(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="主選單：",attachments=[],embeds=[],view=self.parent_view)       # ← 回到原本選單


bot.run(os.environ.get("DISCORD_TOKEN"))
