#splite語法的寫法
import sqlite3

class recordDB:#資料庫的類別
    #設定這個類別的屬性
    def __init__(self,db_name="records.db"):
        self.db_name=db_name
        self.init_db()
    #開始設定方法
    #依物件的名稱建立sqlite連線
    def connect(self):
        return sqlite3.connect(self.db_name)
    #建立資料表
    def init_db(self):
        conn=self.connect()
        cursor=conn.cursor()
        #生成records資料表
        cursor.execute("""CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        today TEXT,
                        item TEXT,
                        amount INTEGER,
                        type TEXT
                        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        discord_id TEXT PRIMARY KEY,
                        password_hash TEXT NOT NULL,
                        is_setup INTEGER DEFAULT 0
                        )""")

        conn.commit()
        conn.close()


    #新增使用這認證資料
    def add_user(self,discord_id,password_hash,is_setup=1):
        conn=self.connect()
        cursor=conn.cursor()
        try:
            cursor.execute("INSERT OR REPLACE INTO users (discord_id,password_hash,is_setup) VALUES (?,?,?)",(discord_id,password_hash,is_setup,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"新增使用者錯誤:{e}")
            return False
        finally:
            conn.close()

    #查詢使用者認證資訊
    def get_user(self,discord_id):
        conn=self.connect()
        cursor=conn.cursor()
        cursor.execute("SELECT password_hash,is_setup FROM users WHERE discord_id=?",(discord_id,))
        user_data=cursor.fetchone()
        conn.close()
        return user_data

    #查詢使用者個人資訊
    def get_profile(self,discord_id):
        conn=self.connect()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE discord_id=?",(discord_id,))
        profile_data=cursor.fetchall()
        conn.close()
        return profile_data

    #新增資料到資料表
    def add_record(self,user_id,today,item,amount,type):
        conn=self.connect()
        cursor=conn.cursor()
        #執行sqlite語法
        cursor.execute("INSERT INTO records (user_id,today,item,amount,type) VALUES(?,?,?,?,?)",(user_id,today,item,amount,type))
        conn.commit()
        conn.close()

    #查詢使用者的所有資料
    def search_records(self,user_id):
        conn=self.connect()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM records WHERE user_id=(?)",(user_id,))
        rows=cursor.fetchall()
        conn.close()
        return rows
    
    #修改某一筆資料的內容
    def edit_record(self,id,user_id,item,amount):
        conn=self.connect()
        cursor=conn.cursor()
        cursor.execute("SELECT user_id FROM records WHERE id=(?)",(id,))
        x=cursor.fetchone()
        print(x[0])
        if x[0]==user_id:
            cursor.execute("UPDATE records SET item=?,amount=? WHERE id=?",(item,amount,id,))
            print("成功")
        else:
            print("失敗")
        conn.commit()
        conn.close()

    #刪除某一筆特定資料
    def delete_record(self,id):
        conn=self.connect()
        cursor=conn.cursor()
        cursor.execute("DELETE FROM records WHERE id=(?)",(id,))
        conn.commit()
        conn.close()







# import psycopg2 #postgres的寫法
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class recordDB:#資料庫的類別
#     #設定這個類別的屬性
#     def __init__(self,db_url=os.environ.get("DATABASE_URL")):
#         self.db_url=db_url
#         self.init_db()
#     #開始設定方法
#     #依物件的名稱建立sqlite連線
#     def connect(self):
#         return psycopg2.connect(self.db_url)
#     #建立資料表
#     def init_db(self):
#         conn=self.connect()
#         cursor=conn.cursor()
#         #執行sqlite語法(splite的依序給key是用INTEGER)
#         cursor.execute("""CREATE TABLE IF NOT EXISTS records (
#                         id SERIAL PRIMARY KEY,
#                         user_id TEXT,
#                         today DATE,
#                         item TEXT,
#                         amount INTEGER,
#                         type TEXT
#                         )""")
#         conn.commit()
#         conn.close()
#     #新增資料到資料表
#     def add_record(self,user_id,today,item,amount,type):
#         conn=self.connect()
#         cursor=conn.cursor()
#         #執行sqlite語法(splite用?,psycopg2用%s)
#         cursor.execute("INSERT INTO records (user_id,today,item,amount,type) VALUES(%s,%s,%s,%s,%s)",(user_id,today,item,amount,type))
#         conn.commit()
#         conn.close()
#     #查詢使用者的所有資料
#     def search_records(self,user_id):
#         conn=self.connect()
#         cursor=conn.cursor()
#         cursor.execute("SELECT * FROM records WHERE user_id=(%s)",(user_id,))
#         rows=cursor.fetchall()
#         conn.close()

        
#         return rows
#     #修改某一筆資料的內容(感覺有點難之後再做)
#     def edit_record(self,id,user_id,item,amount):
#         conn=self.connect()
#         cursor=conn.cursor()
#         cursor.execute("SELECT user_id FROM records WHERE id=(%s)",(id,))
#         x=cursor.fetchone()
#         print(x[0])
#         if x[0]==user_id:
#             cursor.execute("UPDATE records SET item=%s,amount=%s WHERE id=%s",(item,amount,id,))
#             print("成功")
#         else:
#             print("失敗")
#         conn.commit()
#         conn.close()
#     #刪除某一筆特定資料
#     def delete_record(self,id):
#         conn=self.connect()
#         cursor=conn.cursor()
#         cursor.execute("DELETE FROM records WHERE id=(%s)",(id,))
#         conn.commit()
#         conn.close()