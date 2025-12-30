#py-cord套件
import discord
from discord.commands import slash_command #斜線指令套件
from discord.commands import Option #選單套件
from discord import Embed
from discord.ui import Modal,InputText,View
#導入資料庫程式
from database import recordDB
#圖表分析套件
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm # 引入字體管理
#時間套件
import datetime
from datetime import date

plt.rcParams['font.family'] = 'Microsoft JhengHei'#預設圖表中的字體，否則會出現方框

db=recordDB()

#/////////////////////////////////////////////////////////////////////////
#新增紀錄
#/////////////////////////////////////////////////////////////////////////
class add_record_modal(Modal):
    #這得*args跟**kwargs是為了將資料完整傳給父類別
    def __init__(self, parent_view, *args, **kwargs):
        super().__init__(*args, **kwargs, title="新增消費紀錄")
        self.parent_view=parent_view
        # 這是輸入「項目」的欄位
        self.item_input=InputText(
            label="項目名稱 ",
            placeholder="例如：午餐、薪水",
            max_length=50,
            required=True,
            row=0
        )
        # 這是輸入「金額」的欄位
        self.amount_input = InputText(
            label="金額 (請輸入數字)",
            placeholder="例如：100",
            required=True,
            row=1
        )
        # 這是選擇「收支類型」的欄位
        self.type_input = InputText(
            label="收支類型",
            placeholder="輸入：收入 或 支出",
            required=True,
            max_length=5,
            row=2
        )
        # 這是選擇「詳細類型」的欄位
        self.category_input = InputText(
            label="詳細類型",
            placeholder="輸入：食、衣、住、行、育、樂、薪水、其他收入",
            required=True,
            max_length=5,
            row=3
        )
        #將上面的輸入框用add_item放上
        self.add_item(self.item_input)
        self.add_item(self.amount_input)
        self.add_item(self.type_input)
        self.add_item(self.category_input)

    #這邊注意py-cord是用callback，discord.py才是用on_submit
    async def callback(self,interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        #判斷輸入資料是否符合條件，並紀錄資料
        try:
            item=str(self.item_input.value)
            amount=int(self.amount_input.value)
            type=str(self.type_input.value)
            category=str(self.category_input.value)
            if type not in ["收入","支出"]:
                await interaction.followup.send("輸入的收支類型錯誤",ephemeral=False)
                return
            if category not in ["食","衣","住","行","育","樂","薪水","其他收入"]:
                await interaction.followup.send("輸入的詳細類型錯誤",ephemeral=False)
                return
            # 從 parent_view 獲取登入使用者的 user_id
            user_id = self.parent_view.user_id
            if user_id is None:
                user_id = str(interaction.user.id)

            today = datetime.date.today()

            db.add_record(user_id,today,item,amount,type,category)
            await interaction.followup.send("已計入帳本",ephemeral=False)
        except ValueError:
            await interaction.followup.send("請輸入有效數字",ephemeral=False)
        except Exception as e:
            await interaction.followup.send(f"發生錯誤：{e}",ephemeral=False)

#/////////////////////////////////////////////////////////////////////////
#查詢紀錄
#/////////////////////////////////////////////////////////////////////////
class search_records_embed():
    def __init__(self,parent_view):
        self.parent_view=parent_view
    def get_embed(self):
        user_id=self.parent_view.user_id
        rows=db.search_records(user_id)
        #查詢出的資料
        embed = Embed(title="📒 記帳紀錄")
        for r in rows:
            id,user_id,today,item,amount,type,category=r
            embed.add_field(
                name="ID: {:<20d}  {:>20s}".format(id,"📅 "+today),
                value=f"📌 {item} 💵 {amount} 💰 {type}  🔖{category}",
                inline=False
            )
        return embed

#/////////////////////////////////////////////////////////////////////////
#修改紀錄
#/////////////////////////////////////////////////////////////////////////
class edit_record_modal(Modal):
    def __init__(self,parent_view,*args,**kwargs):
        super().__init__(*args,**kwargs,title="修改消費紀錄")
        self.parent_view=parent_view
        # 這是輸入要修改的id
        self.id_input=InputText(
            label="第＿筆記錄 ",
            placeholder='例如：1,2,...,100',
            max_length=50,
            required=True,
            row=0
        )
        # 這是輸入「項目」的欄位
        self.item_input=InputText(
            label="項目名稱 ",
            placeholder='例如：午餐、薪水',
            max_length=50,
            required=True,
            row=1
        )
        # 這是輸入「金額」的欄位
        self.amount_input=InputText(
            label='金額 (請輸入數字)',
            placeholder='例如：100',
            required=True,
            row=2
        )
        # 這是選擇「收支類型」的欄位
        self.type_input=InputText(
            label='收支類型',
            placeholder='輸入：收入 或 支出',
            required=True,
            max_length=5,
            row=3
        )
        # 這是選擇「詳細類型」的欄位
        self.category_input=InputText(
            label='詳細類型',
            placeholder='輸入：食、衣、住、行、育、樂、薪水、額外收入',
            required=True,
            max_length=5,
            row=4
        )
        #將上面的輸入框用add_item放上
        self.add_item(self.id_input)
        self.add_item(self.item_input)
        self.add_item(self.amount_input)
        self.add_item(self.type_input)
        self.add_item(self.category_input)

    async def callback(self,interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            id=self.id_input.value
            print(id)
            user_id=self.parent_view.user_id
            item=str(self.item_input.value)
            amount=int(self.amount_input.value)
            type=str(self.type_input.value)
            category=str(self.category_input.value)

            db.edit_record(id,user_id,item,amount,type,category)
            await interaction.followup.send(f"已修改第{id}筆記錄")
        except ValueError:
            await interaction.followup.send("請輸入有效數字",ephemeral=False)
        except Exception as e:
            await interaction.followup.send(f"發生錯誤：{e}",ephemeral=False)

#/////////////////////////////////////////////////////////////////////////
#刪除紀錄
#/////////////////////////////////////////////////////////////////////////
class delete_record_modal(Modal):
    def __init__(self,parent_view,*args,**kwargs):
        super().__init__(*args,**kwargs,title="刪除消費紀錄")
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
            await interaction.followup.send(f"已刪除第{id}筆記錄")
        except ValueError:
            await interaction.followup.send("請輸入有效數字",ephemeral=False)
        except Exception as e:
            await interaction.followup.send(f"發生錯誤：{e}",ephemeral=False)

#/////////////////////////////////////////////////////////////////////////
#個人資料
#/////////////////////////////////////////////////////////////////////////
class profile_embed():
    def __init__(self,parent_view):
        self.parent_view=parent_view
    def get_embed(self):
        user_id=self.parent_view.user_id
        profile_data=db.get_profile(user_id)
        # 表頭
        embed = Embed(title="🪪 個人資料")

        for i in profile_data:
            discord_id,password_hash,is_setup,target=i
            if is_setup==1:
                emoji="🟢"
                is_setup="已註冊"
            else:
                emoji="🔴"
                is_setup="未註冊"

            embed.add_field(
                name=f"ID: {id}",
                value=f"👤 {discord_id}\n🔐 {password_hash}\n{emoji} {is_setup}\n",
                inline=False
            )
        return embed
#/////////////////////////////////////////////////////////////////////////
#圖表分析
#/////////////////////////////////////////////////////////////////////////
class chart_analysis():
    def __init__(self,parent_view):
        self.parent_view=parent_view
        #收入
        self.income={"收入":0,"薪水":0,"其他收入":0}
        #支出
        self.expense={"支出":0,"食":0,"衣":0,"住":0,"行":0,"育":0,"樂":0}
        #總金額
        self.total=0
        #紀錄有哪些分類有金額(以利後續圖表分析)
        self.tatal_state=[0,0,0,0,0,0,0,0,0,0]#照順序紀錄下列的紀錄

        self.filter_income=[]
        self.filter_expense=[]

    #抓取資料並做出初步的整理
    def get_data(self):
        user_id=self.parent_view.user_id
        analysis_data=db.search_now_month_records(user_id)
        for data in analysis_data:
            id,user_id,today,item,amount,type,category=data[0]
            #記收入
            if type=="收入":
                self.income["收入"]+=amount
                self.tatal_state[0]=1
                if category=="薪水":
                    self.income["薪水"]+=amount
                    self.tatal_state[1]=1
                if category=="其他收入":
                    self.income["其他收入"]+=amount
                    self.tatal_state[2]=1
            #記支出
            if type=="支出":
                self.expense["支出"]+=amount
                self.tatal_state[3]=1
                if category=="食":
                    self.expense["食"]+=amount
                    self.tatal_state[4]=1
                if category=="衣":
                    self.expense["衣"]+=amount
                    self.tatal_state[5]=1
                if category=="住":
                    self.expense["住"]+=amount
                    self.tatal_state[6]=1
                if category=="行":
                    self.expense["行"]+=amount
                    self.tatal_state[7]=1
                if category=="育":
                    self.expense["育"]+=amount
                    self.tatal_state[8]=1
                if category=="樂":
                    self.expense["樂"]+=amount
                    self.tatal_state[9]=1

    #整粒資料
    def analysis_data(self):
        self.get_data()#先抓取原始資料
        # self.total=self.income+self.expense

    #生成圖表
    def creat_chart(self):
        self.analysis_data()#先抓取整理後的資料
        discord_id=self.parent_view.user_id

        #設定字體
        font_path='微軟正黑體-1.ttf'
        my_font = fm.FontProperties(fname=font_path)

        #收支建議
        balance=self.income["收入"]-self.expense["支出"]
        expense_items=list(self.expense.items())
        max_data=dict(expense_items[1:])
        advice_text_ie=""
        if balance>0:
            advice_text_ie=f"🎉 太棒了！本月目前結餘 **{balance}** 元。\n繼續保持，可以考慮將多餘資金存入儲蓄！"
        elif balance==0:
            advice_text_ie="⚖️ 收支平衡！\n雖然沒有超支，但也沒存到錢，下個月加油！"
        else:
            advice_text_ie=f"⚠️ 注意！本月已經超支 **{abs(balance)}** 元了！\n建議檢視「{max(max_data,key=max_data.get)}」類別的花費，減少不必要的支出。"
        
        #目標預算建議
        target=db.search_target(discord_id)
        advice_text_target=""
        if target>self.expense["支出"]:
            advice_text_target=f"🎉 恭喜！近期花費成功控制在 **{target}** 元以內。請繼續保持，注意還有多少於預算可用！"
        elif target==self.expense["支出"]:
            advice_text_target=f"🚫 已達預算上限，請賺多一點錢或節省開銷！"
        else:
            advice_text_target=f"⚠️ 花費已超出預算，請注意「{max(max_data,key=max_data.get)}」這方面的支出！"
        embed_advice=discord.Embed(title="財務分析建議",description=f"收支建議\n{advice_text_ie}\n\n\n目標預算建議\n{advice_text_target}",color=discord.Color.gold())

        try:
            self.filter_income=dict([(k,v) for k,v in zip(self.income.keys(),self.income.values()) if v>0])
            plt.title("收入分析",fontproperties=my_font)
            plt.pie(list(self.filter_income.values())[1:],radius=1,labels=list(self.filter_income.keys())[1:],textprops={'fontproperties': my_font})
            plt.savefig("income.png")
            file_income=discord.File("income.png")
            embed_income=discord.Embed(title="收入圖表")
            embed_income.set_image(url="attachment://income.png")
            plt.close()
        except:
            print(1)
        try:
            self.filter_expense=dict([(k,v) for k,v in zip(self.expense.keys(),self.expense.values()) if v>0])
            plt.title("支出分析",fontproperties=my_font)
            plt.pie(list(self.filter_expense.values())[1:],radius=1,labels=list(self.filter_expense.keys())[1:],textprops={'fontproperties': my_font})
            plt.savefig("expense.png")
            file_expense=discord.File("expense.png")
            embed_expense=discord.Embed(title="支出圖表")
            # if self.expense["支出"]>db.search_target(discord_id):
            #     embed_expense.add_field(name="財務建議：目前已超出預算")
            # else:
            #     embed_expense.add_field(name="財務建議：目前沒超出預算")
            embed_expense.set_image(url="attachment://expense.png")
            plt.close()
        except:
            print(2)

        return file_income,embed_income,file_expense,embed_expense,embed_advice

#/////////////////////////////////////////////////////////////////////////
#目標預算
#/////////////////////////////////////////////////////////////////////////
class target_modal(Modal):
    #這得*args跟**kwargs是為了將資料完整傳給父類別
    def __init__(self, parent_view, *args, **kwargs):
        super().__init__(*args, **kwargs, title="設立目標預算")
        self.parent_view=parent_view
        # 這是輸入「目標預算」的欄位
        self.target_input=InputText(
            label="本月預算多少",
            placeholder="例如：6000,10000",
            max_length=50,
            required=True,
            row=0
        )
        self.add_item(self.target_input)
    async def callback(self,interaction:discord.Interaction):
        try:
            db.add_target(int(self.target_input.value),self.parent_view.user_id)
        except:
            pass
        await interaction.response.send_message("已成功設立目標預算")
