import discord
from discord.commands import slash_command #斜線指令套件
from discord.commands import Option #選單套件
from discord import Embed
from discord.ui import Modal, InputText, View
#導入資料庫程式
from database import recordDB

import datetime
from datetime import date

db=recordDB()

#/////////////////////////////////////////////////////////////////////////
#新增
#/////////////////////////////////////////////////////////////////////////
class add_record_modal(Modal):
    #這得*args跟**kwargs是為了將資料完整傳給父類別
    def __init__(self, parent_view, *args, **kwargs):
        super().__init__(*args, **kwargs, title="新增消費紀錄")
        self.parent_view=parent_view
        # 這是輸入「項目」的欄位
        self.item_input=InputText(
            label="項目名稱 ",
            placeholder='例如：午餐、薪水',
            max_length=50,
            required=True
        )
        # 這是輸入「金額」的欄位
        self.amount_input = InputText(
            label='金額 (請輸入數字)',
            placeholder='例如：100',
            required=True
        )
        # 這是選擇「收支類型」的下拉選單 (這裡用 TextInput 暫代，實際可用 Select)
        self.type_input = InputText(
            label='收支類型',
            placeholder='輸入：收入 或 支出',
            required=True,
            max_length=2
        )
        #將上面的輸入框用add_item放上
        self.add_item(self.item_input)
        self.add_item(self.amount_input)
        self.add_item(self.type_input)

    #這邊注意py-cord是用callback，discord.py才是用on_submit
    async def callback(self,interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        #判斷輸入資料是否符合條件，並紀錄資料
        try:
            item=str(self.item_input.value)
            amount=int(self.amount_input.value)
            type=str(self.type_input.value)
            if type not in ["收入","支出"]:
                await interaction.followup.send("輸入的類型錯誤",ephemeral=False)
                
                
            # 從 parent_view 獲取登入使用者的 user_id
            user_id = self.parent_view.user_id 
            if user_id is None:
                user_id = str(interaction.user.id)

            today = datetime.date.today()

            db.add_record(user_id,today,item,amount,type)
            await interaction.followup.send("已計入帳本",ephemeral=False)
        except ValueError:
            await interaction.followup.send("請輸入有效數字",ephemeral=False)
        except Exception as e:
            await interaction.followup.send(f"發生錯誤：{e}",ephemeral=False)

#/////////////////////////////////////////////////////////////////////////
#查詢
#/////////////////////////////////////////////////////////////////////////
class search_records_embed():
    def __init__(self,parent_view):
        self.parent_view=parent_view
    def get_embed(self):
        user_id=self.parent_view.user_id
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
        return embed

#/////////////////////////////////////////////////////////////////////////
#修改
#/////////////////////////////////////////////////////////////////////////
class edit_record_modal(Modal):
    def __init__(self, parent_view, *args, **kwargs):
        super().__init__(*args, **kwargs, title="修改消費紀錄")
        self.parent_view=parent_view
        # 這是輸入要修改的id
        self.id_input=InputText(
            label="第＿筆記錄 ",
            placeholder='例如：1,2,...,100',
            max_length=50,
            required=True
        )
        # 這是輸入「項目」的欄位
        self.item_input=InputText(
            label="項目名稱 ",
            placeholder='例如：午餐、薪水',
            max_length=50,
            required=True
        )
        # 這是輸入「金額」的欄位
        self.amount_input = InputText(
            label='金額 (請輸入數字)',
            placeholder='例如：100',
            required=True
        )
        # 這是選擇「收支類型」的欄位
        self.type_input = InputText(
            label='收支類型',
            placeholder='輸入：收入 或 支出',
            required=True,
            max_length=2
        )
        #將上面的輸入框用add_item放上
        self.add_item(self.id_input)
        self.add_item(self.item_input)
        self.add_item(self.amount_input)
        self.add_item(self.type_input)
    async def callback(self,interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            id=self.id_input.value
            user_id=self.parent_view
            item=self.item_input.value
            amount=self.amount_input.value
            type=self.type_input.value

            db.edit_record(id,user_id,item,amount,type)
            await interaction.response.send_message(f"已修改第{id}筆記錄")
        except ValueError:
            await interaction.followup.send("請輸入有效數字",ephemeral=False)
        except Exception as e:
            await interaction.followup.send(f"發生錯誤：{e}",ephemeral=False)

#/////////////////////////////////////////////////////////////////////////
#刪除
#/////////////////////////////////////////////////////////////////////////
class delete_record_modal(Modal):
    def __init__(self, parent_view, *args, **kwargs):
        super().__init__(*args, **kwargs, title="刪除消費紀錄")
        self.parent_view=parent_view
        # 這是輸入要刪除的id
        self.id_input=InputText(
            label="第＿筆紀錄",
            placeholder='例如：1,2,...,100',
            max_length=50,
            required=True
        )
        #將上面的輸入框用add_item放上
        self.add_item(self.id_input)

    async def callback(self,interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            id=self.id_input.value
            db.delete_record(id)
            await interaction.followup.send(f"已修改第{id}筆記錄")
        except ValueError:
            await interaction.followup.send("請輸入有效數字",ephemeral=False)
        except Exception as e:
            await interaction.followup.send(f"發生錯誤：{e}",ephemeral=False)

#/////////////////////////////////////////////////////////////////////////
#個資
#/////////////////////////////////////////////////////////////////////////
class profile_embed():
    def __init__(self,parent_view):
        self.parent_view=parent_view
    def get_embed(self):
        user_id=self.parent_view.user_id
        profile_data=db.get_profile(user_id)
        # 表頭
        embed = Embed(title="🪪 個人資料")

        for r in profile_data:
            discord_id,password_hash,is_setup = r
            if is_setup==1:
                emoji="🟢"
                is_setup="已註冊"
            else:
                emoji="🔴"
                is_setup="未註冊"

            embed.add_field(
                name=f"ID: {id}",
                value=f"👤 {discord_id}\n🔐 {password_hash}\n {emoji} {is_setup}",
                inline=False
            )
        return embed


