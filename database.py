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
        #執行sqlite語法
        cursor.execute("""CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        today TEXT,
                        item TEXT,
                        amount INTEGER,
                        type TEXT
                        )""")
        conn.commit()
        conn.close()
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
    #修改某一筆資料的內容(感覺有點難之後再做)
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