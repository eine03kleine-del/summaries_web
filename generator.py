import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import quote, urljoin
import re
import time

# ==========================================
# 設定
# ==========================================
BASE_URL = "https://www.aozora.gr.jp/"
SAVE_DIR = "aozora_summaries"
os.makedirs(SAVE_DIR, exist_ok=True)

# ==========================================
# 関数群
# ==========================================

def get_author_list():
    """作家一覧を取得（修正版）"""
    url = BASE_URL + "index_pages/person_all.html"
    print(f"📥 作家一覧取得中: {url}")
    res = requests.get(url, timeout=10)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")

    authors = []
    # olタグ内のリンクを取得
    for link in soup.select("ol li a"):
        name = link.text.strip()
        href = link.get("href")
        if href:
            # 相対URLを絶対URLに変換
            full_url = urljoin(url, href)
            # アンカーを削除
            full_url = full_url.split('#')[0]
            authors.append((name, full_url))
    
    print(f"✅ 取得した作家数: {len(authors)}")
    
    # デバッグ: 最初の5人のURLを表示
    print("\n📋 サンプルURL:")
    for i, (name, url) in enumerate(authors[:5]):
        print(f"  {i+1}. {name}: {url}")
    
    return authors

def test_author_page(author_url):
    """作家ページが存在するかテスト"""
    try:
        res = requests.get(author_url, timeout=5)
        if res.status_code == 404:
            return False, "404 Not Found"
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        
        # cardsを含むリンクの数をカウント
        cards_links = [a for a in soup.find_all("a", href=True) if "cards" in a.get("href", "")]
        return True, len(cards_links)
    except Exception as e:
        return False, str(e)

def get_works_from_author(author_url):
    """作家ページから作品一覧を取得"""
    try:
        res = requests.get(author_url, timeout=10)
        if res.status_code == 404:
            print(f"  ⚠️ 404 Not Found")
            return []
        
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")

        works = []
        
        # 作品リストを探す（複数のパターンに対応）
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            title = link.get_text(strip=True)
            
            # cardsページへのリンクを探す
            if "cards" in href and title and len(title) > 1:
                full_url = urljoin(author_url, href)
                works.append((title, full_url))
        
        # 重複削除
        seen = set()
        unique_works = []
        for title, url in works:
            if (title, url) not in seen:
                seen.add((title, url))
                unique_works.append((title, url))
                print(f"  ✓ {title}")
        
        return unique_works
        
    except Exception as e:
        print(f"  ⚠️ エラー: {e}")
        return []

def get_text_url_from_card(card_url):
    """カードページからHTMLファイルのURLを取得"""
    try:
        res = requests.get(card_url, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        
        # HTML版へのリンクを探す
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if "files/" in href and ".html" in href:
                return urljoin(card_url, href)
        
        return None
    except Exception as e:
        print(f"    ⚠️ カードページエラー: {e}")
        return None

def extract_text_from_work(work_url):
    """作品URLから本文を取得"""
    try:
        # カードページからHTML版のURLを取得
        text_url = get_text_url_from_card(work_url)
        if not text_url:
            print(f"    ⚠️ HTML版が見つかりません")
            return None
        
        # 本文ページを取得
        res_text = requests.get(text_url, timeout=10)
        res_text.encoding = res_text.apparent_encoding
        soup_text = BeautifulSoup(res_text.text, "html.parser")
        
        # 本文を抽出
        main_text = soup_text.find("div", class_="main_text")
        if not main_text:
            main_text = soup_text.find("body")
        
        if not main_text:
            return None
        
        # テキストを整形
        text = main_text.get_text(separator="\n", strip=True)
        text = re.sub(r'《.*?》', '', text)
        text = re.sub(r'［＃.*?］', '', text)
        text = re.sub(r'｜', '', text)
        
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)
        
        print(f"    ✓ {len(text)}文字取得")
        return text
        
    except Exception as e:
        print(f"    ⚠️ エラー: {e}")
        return None

def summarize_text(text):
    """簡易要約"""
    text = text.replace("\r", "").replace("\n", " ")
    if len(text) > 500:
        return text[:500] + "..."
    return text

def save_summary(author, title, summary):
    """要約をHTMLファイルとして保存"""
    safe_author = quote(author, safe='')
    safe_title = quote(title, safe='')
    author_dir = os.path.join(SAVE_DIR, safe_author)
    os.makedirs(author_dir, exist_ok=True)

    file_path = os.path.join(author_dir, f"{safe_title}.html")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang='ja'>
<head>
    <meta charset='UTF-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {author}</title>
    <style>
        body {{ font-family: "游ゴシック", "Yu Gothic", sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ line-height: 1.8; background: #f5f5f5; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p><strong>著者:</strong> {author}</p>
    <div class="summary">
        <h2>冒頭</h2>
        <p>{summary}</p>
    </div>
    <p><a href="../index.html">← 一覧に戻る</a></p>
</body>
</html>""")
    
    return file_path

# ==========================================
# メイン処理
# ==========================================

def main():
    all_authors = get_author_list()
    
    # 有効な作家を探す
    print(f"\n{'='*60}")
    print("🔍 有効な作家ページを探索中...")
    print(f"{'='*60}\n")
    
    valid_authors = []
    
    # 様々な範囲から試す
    test_ranges = [
        (0, 20, "最初の20人"),
        (50, 70, "50-70番目"),
        (100, 120, "100-120番目"),
        (200, 220, "200-220番目"),
    ]
    
    for start, end, label in test_ranges:
        print(f"\n📍 {label}を確認中...")
        for i in range(start, min(end, len(all_authors))):
            author, url = all_authors[i]
            
            # 短い間隔でテスト
            is_valid, result = test_author_page(url)
            
            if is_valid and result > 0:
                print(f"  ✅ {author}: {result}作品あり")
                valid_authors.append((author, url))
                if len(valid_authors) >= 5:
                    break
            
            time.sleep(0.2)  # サーバー負荷軽減
        
        if len(valid_authors) >= 5:
            break
    
    if not valid_authors:
        print("\n❌ 有効な作家ページが見つかりませんでした。")
        print("💡 青空文庫のURL構造が変更されている可能性があります。")
        return
    
    print(f"\n{'='*60}")
    print(f"✅ 処理対象: {len(valid_authors)}名")
    print(f"{'='*60}\n")
    
    index_entries = []

    for author, author_url in tqdm(valid_authors, desc="作家処理中"):
        print(f"\n👤 {author}")
        print(f"   URL: {author_url}")
        
        works = get_works_from_author(author_url)[:3]
        
        if not works:
            continue
        
        safe_author = quote(author, safe='')
        author_page_name = safe_author + ".html"
        author_page_path = os.path.join(SAVE_DIR, author_page_name)

        author_entries = []
        for title, work_url in works:
            try:
                print(f"\n  📚 {title}")
                text = extract_text_from_work(work_url)
                if not text or len(text) < 100:
                    continue
                
                summary = summarize_text(text)
                path = save_summary(author, title, summary)
                rel_path = os.path.relpath(path, SAVE_DIR).replace("\\", "/")
                author_entries.append(f"        <li><a href='{rel_path}'>{title}</a></li>")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    ⚠️ エラー: {e}")

        if author_entries:
            with open(author_page_path, "w", encoding="utf-8") as f:
                f.write(f"""<!DOCTYPE html>
<html lang='ja'>
<head>
    <meta charset='UTF-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{author} - 作品一覧</title>
    <style>
        body {{ font-family: "游ゴシック", "Yu Gothic", sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
        a {{ text-decoration: none; color: #0066cc; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>{author} - 作品一覧</h1>
    <ul>
{chr(10).join(author_entries)}
    </ul>
    <p><a href="index.html">← トップに戻る</a></p>
</body>
</html>""")
            index_entries.append(f"        <li><a href='{author_page_name}'>{author} ({len(author_entries)}作品)</a></li>")
            print(f"\n  ✅ {len(author_entries)}作品完了")

    # インデックスページ作成
    index_path = os.path.join(SAVE_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang='ja'>
<head>
    <meta charset='UTF-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>青空文庫 要約まとめ</title>
    <style>
        body {{ font-family: "游ゴシック", "Yu Gothic", sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #fafafa; }}
        h1 {{ color: #333; text-align: center; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ margin: 10px 0; padding: 15px; background: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        a {{ text-decoration: none; color: #0066cc; font-size: 18px; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>📚 青空文庫 要約まとめ</h1>
    <p style="text-align: center; color: #666;">青空文庫の作品をあらすじ付きでまとめました</p>
    <ul>
{chr(10).join(index_entries)}
    </ul>
</body>
</html>""")

    print(f"\n{'='*60}")
    print(f"✅ 完了: {len(index_entries)}名の作家")
    print(f"✅ インデックス: {index_path}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()