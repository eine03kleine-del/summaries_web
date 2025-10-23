import os
import sqlite3
import re
from datetime import datetime
from jinja2 import Template

# === 設定 ===
DB_PATH = "summaries.db"  # SQLiteファイルのパス
OUTPUT_DIR = "output_html"  # 出力先ディレクトリ
TEMPLATE_PATH = "template.html"  # HTMLテンプレートのパス

# === HTMLテンプレート ===
# ※外部ファイルを使わない場合はこのテンプレート文字列を使用
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }}({{ author }})要約</title>
  <style>
    body { font-family: sans-serif; line-height: 1.7; margin: 40px; background: #fdfdfd; }
    h1 { color: #222; border-bottom: 2px solid #ccc; padding-bottom: 5px; }
    .meta { color: #666; font-size: 0.9em; margin-bottom: 20px; }
    .summary { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 5px rgba(0,0,0,0.1); white-space: pre-wrap; }
    .source { margin-top: 30px; font-size: 0.85em; color: #555; }
    .source a { color: #0066cc; text-decoration: none; }
  </style>
</head>
<body>
  <h1>{{ title }}({{ author }})要約</h1>

  <div class="meta">
    要約生成日: {{ date }}
  </div>

  <div class="summary">{{ summary }}</div>

  <div class="source">
    出典: <a href="{{ source_url }}" target="_blank" rel="noopener noreferrer">{{ source_url }}</a><br>
    (青空文庫『{{ title }}』{{ author }} 著 より)
  </div>
</body>
</html>
"""

# === 関数定義 ===

def get_all_summaries():
    """データベースからすべての作品データを取得"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT title, author, summary, source_url FROM summaries")
        rows = cur.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"❌ データベースエラー: {e}")
        return []
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return []


def sanitize_filename(filename):
    """ファイル名として安全な文字列に変換"""
    # 使用不可文字を置換
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    # 全角記号も置換
    filename = filename.replace('（', '').replace(')', '')
    # 空白をアンダースコアに
    filename = filename.replace(' ', '_').replace('　', '_')
    # 連続するアンダースコアを1つに
    filename = re.sub(r'_+', '_', filename)
    # 先頭・末尾のアンダースコアを削除
    filename = filename.strip('_')
    # 空文字列の場合はデフォルト名
    if not filename:
        filename = "untitled"
    # 長すぎる場合は切り詰め（拡張子を除いて200文字まで)
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def generate_html(title, author, summary, source_url):
    """HTMLファイルを生成"""
    try:
        # Jinja2のautoescape機能を有効化
        template = Template(HTML_TEMPLATE, autoescape=True)
        html = template.render(
            title=title,
            author=author,
            summary=summary,
            source_url=source_url,
            date=datetime.now().strftime("%Y-%m-%d"),
        )

        # 出力フォルダを作成
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # 安全なファイル名を生成
        safe_title = sanitize_filename(title)
        filename = f"{safe_title}.html"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # HTMLを書き込み
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ {filepath} を生成しました。")
        
    except IOError as e:
        print(f"❌ ファイル書き込みエラー ({title}): {e}")
    except Exception as e:
        print(f"❌ HTML生成エラー ({title}): {e}")


def main():
    """メイン処理"""
    if not os.path.exists(DB_PATH):
        print(f"❌ データベースファイルが見つかりません: {DB_PATH}")
        return

    summaries = get_all_summaries()
    if not summaries:
        print("⚠️ データベースに要約がありません。")
        return

    print(f"📚 {len(summaries)}件の要約を処理します...\n")
    
    success_count = 0
    for title, author, summary, source_url in summaries:
        generate_html(title, author, summary, source_url)
        success_count += 1
    
    print(f"\n✨ 完了: {success_count}件のHTMLファイルを生成しました。")


if __name__ == "__main__":
    main()