# ============================================================
# migrate_database.py - 既存DBを新構造に移行
# ============================================================
import sqlite3
import os

OLD_DB = "summaries.db"
NEW_DB = "summaries_new.db"

def migrate_database():
    """既存のDBを新しい構造に移行"""
    if not os.path.exists(OLD_DB):
        print(f"❌ {OLD_DB} が見つかりません")
        return
    
    # 旧DBから読み込み
    old_conn = sqlite3.connect(OLD_DB)
    old_cur = old_conn.cursor()
    old_cur.execute("SELECT title, author, summary, source_url FROM summaries")
    old_data = old_cur.fetchall()
    old_conn.close()
    
    # 新DBを作成
    new_conn = sqlite3.connect(NEW_DB)
    new_cur = new_conn.cursor()
    
    # 新テーブル作成
    new_cur.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            summary TEXT NOT NULL,
            source_url TEXT,
            year INTEGER,
            genre TEXT,
            length TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    new_cur.execute("CREATE INDEX IF NOT EXISTS idx_title ON summaries(title)")
    new_cur.execute("CREATE INDEX IF NOT EXISTS idx_author ON summaries(author)")
    new_cur.execute("CREATE INDEX IF NOT EXISTS idx_genre ON summaries(genre)")
    
    # データ移行
    for title, author, summary, source_url in old_data:
        new_cur.execute("""
            INSERT INTO summaries (title, author, summary, source_url)
            VALUES (?, ?, ?, ?)
        """, (title, author, summary, source_url))
    
    new_conn.commit()
    new_conn.close()
    
    print(f"✅ {len(old_data)}件のデータを移行しました")
    print(f"✅ 新しいDB: {NEW_DB}")
    print("\n次の手順:")
    print("1. summaries.db をバックアップ")
    print("2. summaries_new.db を summaries.db にリネーム")
    print("3. python generator_v2.py を実行")

if __name__ == "__main__":
    migrate_database()