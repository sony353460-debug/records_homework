import discord
from discord.ext import commands, tasks
import datetime
from database import recordDB
from function import chart_analysis # 導入你原本寫好的分析功能

# 建立一個假的 View，用來「騙」chart_analysis
# 因為 chart_analysis 需要 parent_view.user_id，我們就做一個給它
class MockView:
    def __init__(self, user_id):
        self.user_id = user_id

class MonthlyReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = recordDB()
        self.monthly_report_task.start() # 啟動排程

    def cog_unload(self):
        self.monthly_report_task.cancel()

    # 設定每天晚上 23:00 (11點) 檢查一次
    # 您可以調整時間，例如 time=datetime.time(hour=23, minute=55)
    @tasks.loop(time=datetime.time(hour=23, minute=0)) 
    async def monthly_report_task(self):
        # 1. 檢查「明天」是不是 1 號
        # 如果明天是 1 號，代表「今天」是這個月的最後一天
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        
        if tomorrow.day == 1:
            print(f"今天是 {today} (月底)，開始發送月報表...")
            await self.send_reports()

    async def send_reports(self):
        # 取得所有使用者 ID
        all_users = self.db.get_all_users()

        for user_id in all_users:
            try:
                # 1. 透過 Bot 取得使用者物件 (為了寄私訊)
                user = await self.bot.fetch_user(int(user_id))
                
                if user:
                    print(f"正在生成 {user.name} 的報表...")
                    
                    # 2. 【關鍵魔法】建立假的 View 並帶入 user_id
                    mock_view = MockView(user_id)
                    
                    # 3. 直接呼叫你原本寫好的 chart_analysis
                    # 這邊完全重複利用了 function.py 的邏輯！
                    analysis = chart_analysis(parent_view=mock_view)
                    
                    # 生成圖表 (使用上一則回答修正後的版本，避免 KeyError)
                    file_income, embed_income, file_expense, embed_expense, embed_advice = analysis.creat_chart()

                    # 4. 發送私訊 (DM)
                    # 注意：私訊不能像 Interaction 那樣 edit_original_response
                    # 我們直接 send 就好
                    
                    # 組合要發送的內容
                    # 這裡為了排版漂亮，我們可以分段發，或者放在一起
                    await user.send(
                        content=f"📊 **{datetime.date.today().month} 月份收支月報** 📊\n這是一封自動發送的月結算通知。",
                        files=[file_income, file_expense],
                        embeds=[embed_income, embed_advice, embed_expense]
                    )
                    
            except Exception as e:
                print(f"無法發送報表給 ID {user_id}: {e}")
                # 可能原因：使用者封鎖了機器人私訊，或資料庫有舊 ID

# 這是讓 main.py 載入用的標準寫法
def setup(bot):
    bot.add_cog(MonthlyReport(bot))