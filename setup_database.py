# ============================================================
# setup_database.py - 改善版データベース設計
# ============================================================

import sqlite3
import os
from datetime import datetime

DB_PATH = "summaries.db"

def init_database():
    """データベースとテーブルを作成（改善版）"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 作品テーブル
    cur.execute("""
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
    
    # 検索用インデックス
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_title ON summaries(title)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_author ON summaries(author)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_genre ON summaries(genre)
    """)
    
    # タグテーブル（多対多）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS summary_tags (
            summary_id INTEGER,
            tag_id INTEGER,
            FOREIGN KEY (summary_id) REFERENCES summaries(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (summary_id, tag_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ データベース {DB_PATH} を初期化しました。")


def add_sample_data():
    """サンプルデータを追加（拡張版）"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    samples = [
        {
            "title": "こころ",
            "author": "夏目漱石",
            "year": 1914,
            "genre": "長編小説",
            "length": "長編",
            "summary": """明治時代の学生「私」が、鎌倉の海岸で出会った「先生」との交流を描いた物語。

第一部では、私が先生に惹かれ、親交を深めていく過程が描かれる。先生は知的で魅力的だが、どこか影を抱えている。

第二部では、父の危篤の知らせで帰省した私のもとに、先生から長い遺書が届く。

第三部の遺書では、先生の青春時代の悲劇が明かされる。親友Kとの友情、同じ女性への恋、そして裏切りによってKが自殺に至った経緯が語られる。先生は罪の意識に苦しみ続け、最後は乃木大将の殉死に触発されて自殺を決意する。

人間のエゴイズムと道徳的苦悩を描いた近代文学の傑作。""",
            "source_url": "https://www.aozora.gr.jp/cards/000148/card773.html",
            "tags": ["明治", "友情", "恋愛", "悲劇"]
        },
        {
            "title": "走れメロス",
            "author": "太宰治",
            "year": 1940,
            "genre": "短編小説",
            "length": "短編",
            "summary": """シチリア島の村に住む羊飼いメロスは、妹の結婚式のために町へ出かける。そこで暴君ディオニス王の恐怖政治を知り、激怒して王城に乗り込む。

メロスは処刑を言い渡されるが、妹の結婚式に出席するため3日間の猶予を願い出る。友人セリヌンティウスを人質として残し、必ず戻ると約束する。

帰路、洪水や山賊に遭遇し、疲労困憊するメロスだが、友を裏切れないという信念で走り続ける。日没直前、処刑場に到着したメロスを見て、王は人間の信実を信じるようになり、二人の友情に感動する。

友情と信義をテーマにした短編の名作。""",
            "source_url": "https://www.aozora.gr.jp/cards/000035/card1567.html",
            "tags": ["友情", "信義", "古代"]
        },
        {
            "title": "羅生門",
            "author": "芥川龍之介",
            "year": 1915,
            "genre": "短編小説",
            "length": "短編",
            "summary": """平安時代末期、荒廃した京都。仕事を失った下人は、雨宿りのため羅生門の楼上に上がる。

そこで死体の髪を抜く老婆を見つける。最初は憎悪を感じた下人だが、老婆が「この女は生きるために蛇を干魚と偽って売っていた。自分も生きるために髪を抜いている」と語るのを聞く。

その論理に触発された下人は、「では自分も生きるために」と老婆の着物を剥ぎ取って逃げ去る。

人間のエゴイズムと善悪の相対性を描いた、芥川の代表的な短編小説。""",
            "source_url": "https://www.aozora.gr.jp/cards/000879/card127.html",
            "tags": ["平安", "エゴイズム", "善悪"]
        },
        {
            "title": "銀河鉄道の夜",
            "author": "宮沢賢治",
            "year": 1934,
            "genre": "童話・ファンタジー",
            "length": "中編",
            "summary": """貧しい少年ジョバンニは、病気の母を支えるため働いている。銀河の祭りの夜、親友カムパネルラと再会する。

ジョバンニが丘で目を覚ますと、銀河鉄道に乗っていた。隣にはカムパネルラがいる。二人は幻想的な銀河の旅を続け、様々な乗客と出会う。

やがてカムパネルラは「ここで降りる」と告げて姿を消す。目覚めたジョバンニは、カムパネルラが川で溺れた友人を助けようとして命を落としたことを知る。

生と死、友情と献身をテーマにした、賢治の未完の傑作。幻想的な描写と深い哲学性が魅力。""",
            "source_url": "https://www.aozora.gr.jp/cards/000081/card456.html",
            "tags": ["ファンタジー", "友情", "献身", "生死"]
        },
        {
            "title": "人間失格",
            "author": "太宰治",
            "year": 1948,
            "genre": "長編小説",
            "length": "長編",
            "summary": """「恥の多い生涯を送って来ました」という告白から始まる主人公・大庭葉蔵の手記。

幼少期から人間社会に馴染めず、道化を演じることで生き延びてきた葉蔵。美術学校に進学するも、酒と女に溺れ、共産主義運動に関わり、心中未遂事件を起こす。

薬物依存に陥り、精神病院に入院。最後は田舎の廃人のような生活を送ることになる。

「自分は人間を理解できない」という孤独と絶望を描いた、太宰の自伝的要素が強い作品。戦後文学を代表する問題作。""",
            "source_url": "https://www.aozora.gr.jp/cards/000035/card301.html",
            "tags": ["昭和", "孤独", "自伝的"]
        }
    ]
    
    for data in samples:
        # 作品を追加
        cur.execute("""
            INSERT INTO summaries (title, author, summary, source_url, year, genre, length)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data["title"], data["author"], data["summary"], data["source_url"], 
              data["year"], data["genre"], data["length"]))
        
        summary_id = cur.lastrowid
        
        # タグを追加
        for tag_name in data["tags"]:
            cur.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
            cur.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_id = cur.fetchone()[0]
            cur.execute("INSERT INTO summary_tags (summary_id, tag_id) VALUES (?, ?)", 
                       (summary_id, tag_id))
    
    conn.commit()
    conn.close()
    print(f"✅ {len(samples)}件のサンプルデータを追加しました。")


if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        response = input(f"⚠️ {DB_PATH} は既に存在します。初期化しますか? (yes/no): ")
        if response.lower() != "yes":
            print("処理を中止しました。")
            exit()
        os.remove(DB_PATH)
    
    init_database()
    add_sample_data()
    print("\n次のコマンドでHTMLを生成できます:")
    print("python generator.py")


# ============================================================
# generator.py - 改善版HTML生成
# ============================================================

"""
import os
import sqlite3
import re
from datetime import datetime
from jinja2 import Template

DB_PATH = "summaries.db"
OUTPUT_DIR = "output_html"

# 個別ページテンプレート
DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }}({{ author }})要約 | 青空文庫要約集</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif; line-height: 1.8; background: #f5f5f5; }
    header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
    header h1 { font-size: 1.5em; }
    header a { color: #3498db; text-decoration: none; }
    nav { background: #34495e; padding: 10px 20px; }
    nav a { color: white; text-decoration: none; margin-right: 20px; }
    nav a:hover { text-decoration: underline; }
    main { max-width: 800px; margin: 40px auto; padding: 0 20px; }
    .work-header { background: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .work-header h2 { font-size: 2em; color: #2c3e50; margin-bottom: 10px; }
    .work-meta { color: #666; font-size: 0.9em; margin-bottom: 15px; }
    .work-meta span { margin-right: 15px; }
    .tags { margin-top: 10px; }
    .tag { display: inline-block; background: #3498db; color: white; padding: 3px 10px; border-radius: 3px; font-size: 0.85em; margin-right: 5px; }
    .summary-box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .summary-box h3 { color: #2c3e50; margin-bottom: 15px; border-left: 4px solid #3498db; padding-left: 10px; }
    .summary-text { white-space: pre-wrap; color: #333; line-height: 2; }
    .source-box { background: #ecf0f1; padding: 20px; border-radius: 8px; font-size: 0.9em; }
    .source-box a { color: #2980b9; text-decoration: none; }
    .source-box a:hover { text-decoration: underline; }
    footer { text-align: center; padding: 30px; color: #777; font-size: 0.9em; }
  </style>
</head>
<body>
  <header>
    <h1>📚 青空文庫要約集</h1>
    <p><a href="index.html">← トップページに戻る</a></p>
  </header>
  
  <nav>
    <a href="index.html">全作品</a>
    <a href="by_author.html">著者別</a>
    <a href="by_genre.html">ジャンル別</a>
  </nav>

  <main>
    <div class="work-header">
      <h2>{{ title }}</h2>
      <div class="work-meta">
        <span>👤 {{ author }}</span>
        <span>📅 {{ year }}年</span>
        <span>📖 {{ genre }}</span>
        <span>📏 {{ length }}</span>
      </div>
      <div class="tags">
        {% for tag in tags %}
        <span class="tag">{{ tag }}</span>
        {% endfor %}
      </div>
    </div>

    <div class="summary-box">
      <h3>📝 あらすじ・要約</h3>
      <div class="summary-text">{{ summary }}</div>
    </div>

    <div class="source-box">
      <strong>📚 原文を読む:</strong><br>
      <a href="{{ source_url }}" target="_blank" rel="noopener noreferrer">{{ source_url }}</a><br>
      <small>青空文庫『{{ title }}』{{ author }} 著</small>
    </div>
  </main>

  <footer>
    <p>© 2025 青空文庫要約集 | 最終更新: {{ date }}</p>
  </footer>
</body>
</html>
'''

# 索引ページテンプレート
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>青空文庫要約集 - 日本文学の名作をわかりやすく</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif; line-height: 1.8; background: #f5f5f5; }
    header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 20px; text-align: center; }
    header h1 { font-size: 2.5em; margin-bottom: 10px; }
    header p { font-size: 1.1em; opacity: 0.9; }
    nav { background: #34495e; padding: 15px 20px; text-align: center; }
    nav a { color: white; text-decoration: none; margin: 0 20px; font-weight: bold; }
    nav a:hover { text-decoration: underline; }
    .stats { max-width: 1000px; margin: 30px auto; padding: 20px; text-align: center; }
    .stats span { display: inline-block; margin: 0 20px; font-size: 1.2em; color: #555; }
    .stats strong { color: #667eea; font-size: 1.5em; }
    main { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
    .search-box { background: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .search-box input { width: 100%; padding: 12px; font-size: 1em; border: 2px solid #ddd; border-radius: 4px; }
    .works-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
    .work-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s; }
    .work-card:hover { transform: translateY(-5px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
    .work-card h3 { color: #2c3e50; margin-bottom: 8px; font-size: 1.3em; }
    .work-card .author { color: #666; font-size: 0.9em; margin-bottom: 10px; }
    .work-card .meta { color: #999; font-size: 0.85em; margin-bottom: 10px; }
    .work-card .excerpt { color: #555; font-size: 0.9em; line-height: 1.6; margin-bottom: 15px; }
    .work-card a { display: inline-block; background: #667eea; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; font-size: 0.9em; }
    .work-card a:hover { background: #5568d3; }
    footer { text-align: center; padding: 40px 20px; color: #777; background: white; margin-top: 40px; }
  </style>
</head>
<body>
  <header>
    <h1>📚 青空文庫要約集</h1>
    <p>日本文学の名作を、わかりやすい要約で</p>
  </header>

  <nav>
    <a href="index.html">全作品</a>
    <a href="by_author.html">著者別</a>
    <a href="by_genre.html">ジャンル別</a>
  </nav>

  <div class="stats">
    <span><strong>{{ total_works }}</strong> 作品</span>
    <span><strong>{{ total_authors }}</strong> 著者</span>
    <span><strong>{{ total_genres }}</strong> ジャンル</span>
  </div>

  <main>
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="🔍 作品名や著者名で検索...">
    </div>

    <div class="works-grid" id="worksGrid">
      {% for work in works %}
      <div class="work-card" data-title="{{ work.title }}" data-author="{{ work.author }}">
        <h3>{{ work.title }}</h3>
        <div class="author">👤 {{ work.author }}</div>
        <div class="meta">📅 {{ work.year }}年 | 📖 {{ work.genre }}</div>
        <div class="excerpt">{{ work.excerpt }}...</div>
        <a href="{{ work.filename }}">続きを読む →</a>
      </div>
      {% endfor %}
    </div>
  </main>

  <footer>
    <p>© 2025 青空文庫要約集</p>
    <p>最終更新: {{ date }}</p>
  </footer>

  <script>
    document.getElementById('searchInput').addEventListener('input', function(e) {
      const query = e.target.value.toLowerCase();
      const cards = document.querySelectorAll('.work-card');
      
      cards.forEach(card => {
        const title = card.dataset.title.toLowerCase();
        const author = card.dataset.author.toLowerCase();
        
        if (title.includes(query) || author.includes(query)) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  </script>
</body>
</html>
'''


def sanitize_filename(filename):
    filename = re.sub(r'[\\\\/:*?"<>|]', '_', filename)
    filename = filename.replace('(', '').replace(')', '')
    filename = filename.replace(' ', '_').replace('　', '_')
    filename = re.sub(r'_+', '_', filename).strip('_')
    return filename[:200] if filename else "untitled"


def get_all_summaries_with_tags():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute('''
            SELECT s.*, GROUP_CONCAT(t.name, ',') as tags
            FROM summaries s
            LEFT JOIN summary_tags st ON s.id = st.summary_id
            LEFT JOIN tags t ON st.tag_id = t.id
            GROUP BY s.id
            ORDER BY s.author, s.year
        ''')
        
        rows = cur.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"❌ データベースエラー: {e}")
        return []


def generate_detail_page(work):
    template = Template(DETAIL_TEMPLATE, autoescape=True)
    tags = work['tags'].split(',') if work['tags'] else []
    
    html = template.render(
        title=work['title'],
        author=work['author'],
        year=work['year'] or '不明',
        genre=work['genre'] or '分類なし',
        length=work['length'] or '不明',
        summary=work['summary'],
        source_url=work['source_url'],
        tags=tags,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    safe_title = sanitize_filename(work['title'])
    filename = f"{safe_title}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    
    return filename


def generate_index_page(works):
    template = Template(INDEX_TEMPLATE, autoescape=True)
    
    works_data = []
    for work in works:
        excerpt = work['summary'][:100].replace('\\n', ' ')
        works_data.append({
            'title': work['title'],
            'author': work['author'],
            'year': work['year'] or '不明',
            'genre': work['genre'] or '分類なし',
            'excerpt': excerpt,
            'filename': sanitize_filename(work['title']) + '.html'
        })
    
    authors = set(w['author'] for w in works)
    genres = set(w['genre'] for w in works if w['genre'])
    
    html = template.render(
        works=works_data,
        total_works=len(works),
        total_authors=len(authors),
        total_genres=len(genres),
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    filepath = os.path.join(OUTPUT_DIR, "index.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 索引ページを生成: {filepath}")


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ データベースファイルが見つかりません: {DB_PATH}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    works = get_all_summaries_with_tags()
    if not works:
        print("⚠️ データベースに要約がありません。")
        return

    print(f"📚 {len(works)}件の作品を処理します...\\n")
    
    for work in works:
        generate_detail_page(work)
    
    generate_index_page(works)
    
    print(f"\\n✨ 完了: {len(works)}件のHTMLファイルと索引ページを生成しました。")
    print(f"\\n🌐 ブラウザで開く: {os.path.join(OUTPUT_DIR, 'index.html')}")


if __name__ == "__main__":
    main()
"""