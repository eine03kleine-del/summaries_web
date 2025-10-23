# ============================================================
# generator_v2.py - 500作品対応版ジェネレーター
# ============================================================

import os
import sqlite3
import re
import json
from datetime import datetime
from jinja2 import Template
from urllib.parse import quote

DB_PATH = "summaries.db"
OUTPUT_DIR = "aozora_summaries"

# ============================================================
# テンプレート
# ============================================================

# 個別作品ページ
WORK_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{{ title }}({{ author }})のあらすじ・要約。青空文庫の作品をわかりやすく紹介。">
  <title>{{ title }}({{ author }}) - LitLite -要約文庫-</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif; line-height: 1.8; background: #f8f9fa; color: #333; }
    header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    header .container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
    header h1 { font-size: 1.5em; }
    header a { color: white; text-decoration: none; opacity: 0.9; }
    header a:hover { opacity: 1; text-decoration: underline; }
    nav { background: #34495e; padding: 15px; }
    nav .container { max-width: 1200px; margin: 0 auto; display: flex; gap: 20px; flex-wrap: wrap; }
    nav a { color: white; text-decoration: none; padding: 5px 10px; border-radius: 4px; }
    nav a:hover { background: rgba(255,255,255,0.1); }
    main { max-width: 900px; margin: 40px auto; padding: 0 20px; }
    .breadcrumb { margin-bottom: 20px; font-size: 0.9em; color: #666; }
    .breadcrumb a { color: #667eea; text-decoration: none; }
    .work-card { background: white; border-radius: 12px; padding: 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px; }
    .work-header h2 { font-size: 2.2em; color: #2c3e50; margin-bottom: 15px; line-height: 1.4; }
    .work-meta { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px; font-size: 0.95em; color: #555; }
    .work-meta span { display: flex; align-items: center; gap: 5px; }
    .summary-section { margin-top: 30px; }
    .summary-section h3 { color: #667eea; margin-bottom: 15px; font-size: 1.3em; border-left: 4px solid #667eea; padding-left: 12px; }
    .summary-text { white-space: pre-wrap; line-height: 2; font-size: 1.05em; }
    .source-box { background: #f0f4ff; padding: 25px; border-radius: 8px; margin-top: 30px; }
    .source-box h3 { color: #667eea; margin-bottom: 15px; font-size: 1.1em; }
    .source-box a { color: #667eea; word-break: break-all; }
    footer { background: #2c3e50; color: white; padding: 40px 20px; text-align: center; margin-top: 60px; }
    @media (max-width: 768px) {
      header h1 { font-size: 1.2em; }
      .work-header h2 { font-size: 1.6em; }
      main { padding: 0 15px; }
      .work-card { padding: 25px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="container">
      <h1>LitLite -要約文庫-</h1>
      <a href="index.html">トップへ</a>
    </div>
  </header>
  
  <nav>
    <div class="container">
      <a href="index.html">全作品</a>
      <a href="by_author.html">著者別</a>
      <a href="by_year.html">年代別</a>
      <a href="by_genre.html">ジャンル別</a>
    </div>
  </nav>

  <main>
    <div class="breadcrumb">
      <a href="index.html">トップ</a> &gt; 
      <a href="by_author.html#{{ author }}">{{ author }}</a> &gt; 
      {{ title }}
    </div>

    <article class="work-card">
      <div class="work-header">
        <h2>{{ title }}</h2>
        <div class="work-meta">
          <span>👤 {{ author }}</span>
          {% if year %}<span>📅 {{ year }}年</span>{% endif %}
          {% if genre %}<span>📖 {{ genre }}</span>{% endif %}
          {% if length %}<span>📏 {{ length }}</span>{% endif %}
        </div>
      </div>

      <div class="summary-section">
        <h3>📝 あらすじ・要約</h3>
        <div class="summary-text">{{ summary }}</div>
      </div>

      <div class="source-box">
        <h3>📚 原文を読む</h3>
        <p><a href="{{ source_url }}" target="_blank" rel="noopener noreferrer">{{ source_url }}</a></p>
        <p style="margin-top: 10px; font-size: 0.9em; color: #666;">青空文庫『{{ title }}』{{ author }} 著</p>
      </div>
    </article>
  </main>

  <footer>
    <p>&copy; 2025 LitLite -要約文庫-</p>
    <p style="margin-top: 10px; opacity: 0.8;">最終更新: {{ date }}</p>
  </footer>
</body>
</html>'''

# トップページ（全作品一覧）
INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="青空文庫の名作{{ total_works }}作品のあらすじ・要約をわかりやすく紹介。夏目漱石、太宰治、芥川龍之介など日本文学の傑作を網羅。">
  <title>LitLite -要約文庫-{{ total_works }}作品</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif; line-height: 1.8; background: #f8f9fa; }
    header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 20px; text-align: center; }
    header h1 { font-size: 2.8em; margin-bottom: 15px; }
    header p { font-size: 1.2em; opacity: 0.95; }
    nav { background: #34495e; padding: 15px; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    nav .container { max-width: 1200px; margin: 0 auto; display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; }
    nav a { color: white; text-decoration: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
    nav a:hover { background: rgba(255,255,255,0.2); }
    .stats { max-width: 1200px; margin: 40px auto; padding: 0 20px; display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; }
    .stat-box { text-align: center; }
    .stat-box .number { font-size: 2.5em; color: #667eea; font-weight: bold; }
    .stat-box .label { color: #666; margin-top: 5px; }
    main { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
    .search-box { background: white; padding: 25px; border-radius: 12px; margin-bottom: 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .search-box input { width: 100%; padding: 15px 20px; font-size: 1.1em; border: 2px solid #e0e0e0; border-radius: 8px; }
    .search-box input:focus { outline: none; border-color: #667eea; }
    .filter-tabs { margin-bottom: 30px; display: flex; gap: 10px; flex-wrap: wrap; }
    .filter-tabs button { padding: 10px 20px; border: none; background: white; border-radius: 20px; cursor: pointer; font-size: 1em; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .filter-tabs button.active { background: #667eea; color: white; }
    .works-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 25px; }
    .work-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s; }
    .work-card:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.15); }
    .work-card h3 { color: #2c3e50; margin-bottom: 10px; font-size: 1.4em; line-height: 1.4; }
    .work-card .author { color: #667eea; font-weight: bold; margin-bottom: 10px; }
    .work-card .meta { color: #999; font-size: 0.9em; margin-bottom: 15px; }
    .work-card .excerpt { color: #555; line-height: 1.7; margin-bottom: 20px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
    .work-card a { display: inline-block; background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; }
    .work-card a:hover { background: #5568d3; }
    .no-results { text-align: center; padding: 60px 20px; color: #999; font-size: 1.2em; }
    footer { background: #2c3e50; color: white; padding: 40px 20px; text-align: center; margin-top: 80px; }
    @media (max-width: 768px) {
      header h1 { font-size: 2em; }
      .stats { gap: 20px; }
      .works-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>LitLite -要約文庫-</h1>
    <p>名作を、わかりやすい要約で。</p>
  </header>

  <nav>
    <div class="container">
      <a href="index.html">全作品</a>
      <a href="by_author.html">著者別</a>
      <a href="by_year.html">年代別</a>
      <a href="by_genre.html">ジャンル別</a>
    </div>
  </nav>

  <div class="stats">
    <div class="stat-box">
      <div class="number">{{ total_works }}</div>
      <div class="label">作品</div>
    </div>
    <div class="stat-box">
      <div class="number">{{ total_authors }}</div>
      <div class="label">著者</div>
    </div>
    <div class="stat-box">
      <div class="number">{{ total_genres }}</div>
      <div class="label">ジャンル</div>
    </div>
  </div>

  <main>
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="🔍 作品名や著者名で検索...">
    </div>

    <div class="works-grid" id="worksGrid">
      {% for work in works %}
      <article class="work-card" data-title="{{ work.title }}" data-author="{{ work.author }}" data-genre="{{ work.genre }}">
        <h3>{{ work.title }}</h3>
        <div class="author">{{ work.author }}</div>
        <div class="meta">
          {% if work.year %}📅 {{ work.year }}年{% endif %}
          {% if work.genre %} | 📖 {{ work.genre }}{% endif %}
        </div>
        <div class="excerpt">{{ work.excerpt }}</div>
        <a href="{{ work.filename }}">続きを読む →</a>
      </article>
      {% endfor %}
    </div>

    <div class="no-results" id="noResults" style="display: none;">
      該当する作品が見つかりませんでした
    </div>
  </main>

  <footer>
    <p>&copy; 2025 LitLite -要約文庫-</p>
    <p style="margin-top: 10px; opacity: 0.8;">最終更新: {{ date }}</p>
  </footer>

  <script>
    const searchInput = document.getElementById('searchInput');
    const worksGrid = document.getElementById('worksGrid');
    const noResults = document.getElementById('noResults');

    searchInput.addEventListener('input', function() {
      const query = this.value.toLowerCase().trim();
      const cards = worksGrid.querySelectorAll('.work-card');
      let visibleCount = 0;

      cards.forEach(card => {
        const title = card.dataset.title.toLowerCase();
        const author = card.dataset.author.toLowerCase();
        
        if (title.includes(query) || author.includes(query)) {
          card.style.display = 'block';
          visibleCount++;
        } else {
          card.style.display = 'none';
        }
      });

      noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    });
  </script>
</body>
</html>'''

# 著者別一覧ページ
AUTHOR_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>著者別一覧 - LitLite -要約文庫-</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif; background: #f8f9fa; }
    header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }
    header h1 { font-size: 2.2em; }
    nav { background: #34495e; padding: 15px; position: sticky; top: 0; z-index: 100; }
    nav .container { max-width: 1200px; margin: 0 auto; display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; }
    nav a { color: white; text-decoration: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
    nav a:hover { background: rgba(255,255,255,0.2); }
    main { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
    .author-section { background: white; padding: 30px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .author-section h2 { color: #2c3e50; margin-bottom: 20px; font-size: 1.8em; border-bottom: 3px solid #667eea; padding-bottom: 10px; }
    .works-list { display: grid; gap: 15px; }
    .work-item { padding: 15px; border-left: 4px solid #667eea; background: #f8f9fa; border-radius: 4px; }
    .work-item a { color: #667eea; text-decoration: none; font-size: 1.1em; font-weight: bold; }
    .work-item a:hover { text-decoration: underline; }
    .work-item .meta { color: #999; font-size: 0.9em; margin-top: 5px; }
    footer { background: #2c3e50; color: white; padding: 40px 20px; text-align: center; margin-top: 80px; }
  </style>
</head>
<body>
  <header>
    <h1>📝 著者別一覧</h1>
  </header>

  <nav>
    <div class="container">
      <a href="index.html">全作品</a>
      <a href="by_author.html">著者別</a>
      <a href="by_year.html">年代別</a>
      <a href="by_genre.html">ジャンル別</a>
    </div>
  </nav>

  <main>
    {% for author_name, works in authors.items() %}
    <section class="author-section" id="{{ author_name }}">
      <h2>{{ author_name }} ({{ works|length }}作品)</h2>
      <div class="works-list">
        {% for work in works %}
        <div class="work-item">
          <a href="{{ work.filename }}">{{ work.title }}</a>
          <div class="meta">
            {% if work.year %}{{ work.year }}年{% endif %}
            {% if work.genre %} | {{ work.genre }}{% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
    </section>
    {% endfor %}
  </main>

  <footer>
    <p>&copy; 2025 LitLite -要約文庫-</p>
  </footer>
</body>
</html>'''


# ============================================================
# 関数
# ============================================================

def sanitize_filename(text):
    text = re.sub(r'[\\\\/:*?"<>|]', '', text)
    text = text.replace('(', '').replace(')', '').replace(' ', '_').replace('　', '_')
    text = re.sub(r'_+', '_', text).strip('_')
    # 日本語を含むファイル名をそのまま使用（URLエンコード対策）
    return text[:100] if text else "untitled"


def get_all_works():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM summaries ORDER BY author, year")
        rows = [dict(row) for row in cur.fetchall()]
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"❌ DBエラー: {e}")
        return []


def generate_work_page(work):
    template = Template(WORK_TEMPLATE, autoescape=True)
    html = template.render(
        title=work['title'],
        author=work['author'],
        year=work.get('year'),
        genre=work.get('genre'),
        length=work.get('length'),
        summary=work['summary'],
        source_url=work['source_url'],
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    filename = f"{sanitize_filename(work['title'])}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    
    return filename


def generate_index(works):
    works_data = []
    for work in works:
        excerpt = work['summary'][:80].replace('\\n', ' ') + '...'
        works_data.append({
            'title': work['title'],
            'author': work['author'],
            'year': work.get('year'),
            'genre': work.get('genre'),
            'excerpt': excerpt,
            'filename': f"{sanitize_filename(work['title'])}.html"
        })
    
    authors = set(w['author'] for w in works)
    genres = set(w.get('genre') for w in works if w.get('genre'))
    
    template = Template(INDEX_TEMPLATE, autoescape=True)
    html = template.render(
        works=works_data,
        total_works=len(works),
        total_authors=len(authors),
        total_genres=len(genres),
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def generate_author_index(works):
    authors_dict = {}
    for work in works:
        author = work['author']
        if author not in authors_dict:
            authors_dict[author] = []
        authors_dict[author].append({
            'title': work['title'],
            'year': work.get('year'),
            'genre': work.get('genre'),
            'filename': f"{sanitize_filename(work['title'])}.html"
        })
    
    # 著者名でソート
    authors_dict = dict(sorted(authors_dict.items()))
    
    template = Template(AUTHOR_TEMPLATE, autoescape=True)
    html = template.render(authors=authors_dict)
    
    with open(os.path.join(OUTPUT_DIR, "by_author.html"), "w", encoding="utf-8") as f:
        f.write(html)


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ {DB_PATH} が見つかりません")
        print("まず migrate_database.py を実行してください")
        return
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    works = get_all_works()
    if not works:
        print("⚠️ データがありません")
        return
    
    print(f"📚 {len(works)}件を処理中...\\n")
    
    # 各作品ページ生成
    for work in works:
        generate_work_page(work)
        print(f"✅ {work['title']}")
    
    # 索引ページ生成
    generate_index(works)
    print(f"\\n✅ トップページ生成")
    
    generate_author_index(works)
    print(f"✅ 著者別ページ生成")
    
    print(f"\\n✨ 完了: {len(works)}作品 + 索引ページを生成")
    print(f"🌐 確認: {OUTPUT_DIR}/index.html")


if __name__ == "__main__":
    main()