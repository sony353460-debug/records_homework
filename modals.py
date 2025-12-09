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




########目前要修的城市，輸入資料按完確定後這邊沒反應
    async def callback(self,interaction:discord.Interaction):
        print("!!!!!")
        #判斷輸入資料是否符合條件，並紀錄資料
        try:
            item=str(self.item_input.value)
            amount=int(self.amount_input.value)
            type=str(self.type_input.value)
            if type not in ["收入","支出"]:
                await interaction.response.send_message("輸入的類型錯誤",ephemeral=False)
                
                
            # ✅ 修正 1：從 parent_view 獲取登入使用者的 user_id
            user_id = self.parent_view.user_id 
            if user_id is None:
                user_id = str(interaction.user.id)

            today = datetime.date.today()

            db.add_record(user_id,today,item,amount,type)
            await interaction.response.send_message("已計入帳本",ephemeral=False)
        #出現數值錯誤
        except ValueError:
            await interaction.response.send_message("請輸入有效數字",ephemeral=False)
        except Exception as e:
            await interaction.response.send_message(f"發生錯誤：{e}",ephemeral=False)