#!/usr/bin/env python
# coding: utf-8

# ライブラリのインポート
import os
import sys
import tkinter as tk
import webbrowser
from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from apiclient.discovery import build

from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, YOUTUBE_API_KEY

# Windowsでコンソールウィンドウを非表示にする
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Spotify API の初期化
client_credentials_manager = SpotifyClientCredentials(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager, language='ja')


# アーティスト名入力ウィンドウ
def get_artist_name():
    def on_submit():
        artist_name.set(entry.get())
        root.destroy()

    def on_hover(e):
        submit_button.configure(bg="#1DB954")

    def on_leave(e):
        submit_button.configure(bg="#1ED760")

    root = tk.Tk()
    root.title("🎵 Music Search")

    # ウィンドウサイズと位置（中央配置）
    window_width, window_height = 450, 280
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_pos = (screen_width // 2) - (window_width // 2)
    y_pos = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
    root.resizable(False, False)

    # グラデーション風の背景色
    root.configure(bg="#1a1a2e")

    artist_name = tk.StringVar()

    # タイトルラベル
    title_label = tk.Label(
        root,
        text="🎵 Music Search",
        font=("Segoe UI", 20, "bold"),
        bg="#1a1a2e",
        fg="#ffffff"
    )
    title_label.pack(pady=(30, 10))

    # サブタイトルラベル
    subtitle_label = tk.Label(
        root,
        text="お気に入りのアーティストを検索",
        font=("Meiryo UI", 10),
        bg="#1a1a2e",
        fg="#aaaaaa"
    )
    subtitle_label.pack(pady=(0, 20))

    # エントリーフレーム（影風の効果）
    entry_frame = tk.Frame(root, bg="#16213e", bd=0)
    entry_frame.pack(pady=10)

    # エントリーウィジェット
    entry = tk.Entry(
        entry_frame,
        textvariable=artist_name,
        font=("Meiryo UI", 14),
        bg="#16213e",
        fg="#ffffff",
        insertbackground="#1ED760",
        relief="flat",
        bd=0,
        width=25
    )
    entry.pack(padx=15, pady=15)
    entry.focus_set()

    # 送信ボタン（Spotify風のグリーン）
    submit_button = tk.Button(
        root,
        text="検 索",
        command=on_submit,
        font=("Meiryo UI", 12, "bold"),
        bg="#1ED760",
        fg="#000000",
        activebackground="#1DB954",
        activeforeground="#000000",
        relief="flat",
        bd=0,
        padx=40,
        pady=12,
        cursor="hand2"
    )
    submit_button.pack(pady=20)

    # ホバーエフェクト
    submit_button.bind("<Enter>", on_hover)
    submit_button.bind("<Leave>", on_leave)

    # Enterキーで送信
    root.bind("<Return>", lambda event: on_submit())

    root.mainloop()

    return artist_name.get()


# HTMLを生成する関数
def generate_html(artist, tracks_data):
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{artist} - Top Tracks</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0a0e27;
            color: #ffffff;
            padding: 60px 20px;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }}

        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 50%, rgba(30, 215, 96, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(29, 185, 84, 0.1) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }}

        header {{
            text-align: center;
            margin-bottom: 60px;
        }}

        h1 {{
            font-size: 4rem;
            font-weight: 900;
            margin-bottom: 15px;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #1ED760 0%, #1DB954 50%, #17a348 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: fadeInDown 0.8s ease;
        }}

        .subtitle {{
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.95rem;
            font-weight: 300;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }}

        .track-list {{
            display: grid;
            gap: 16px;
        }}

        .track-card {{
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 24px;
            display: flex;
            align-items: center;
            gap: 24px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(255, 255, 255, 0.05);
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.6s ease backwards;
        }}

        .track-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(30, 215, 96, 0.1) 0%, transparent 50%);
            opacity: 0;
            transition: opacity 0.4s ease;
            pointer-events: none;
        }}

        .track-card:hover {{
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(30, 215, 96, 0.3);
            transform: translateX(8px);
        }}

        .track-card:hover::before {{
            opacity: 1;
        }}

        .rank {{
            font-size: 1.8rem;
            font-weight: 700;
            color: rgba(255, 255, 255, 0.3);
            min-width: 45px;
            text-align: center;
            transition: all 0.3s ease;
        }}

        .track-card:hover .rank {{
            color: #1ED760;
            transform: scale(1.1);
        }}

        .album-cover {{
            width: 100px;
            height: 100px;
            border-radius: 12px;
            object-fit: cover;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            transition: all 0.4s ease;
        }}

        .track-card:hover .album-cover {{
            transform: scale(1.05);
            box-shadow: 0 12px 32px rgba(30, 215, 96, 0.3);
        }}

        .track-info {{
            flex: 1;
            min-width: 0;
        }}

        .track-name {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .track-meta {{
            display: flex;
            gap: 20px;
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.875rem;
            font-weight: 400;
            margin-bottom: 12px;
        }}

        .popularity-container {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .popularity-bar {{
            flex: 1;
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
            overflow: hidden;
        }}

        .popularity-fill {{
            height: 100%;
            background: linear-gradient(90deg, #1ED760 0%, #1DB954 100%);
            border-radius: 2px;
            transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .popularity-value {{
            font-size: 0.875rem;
            font-weight: 600;
            color: #1ED760;
            min-width: 35px;
        }}

        .actions {{
            display: flex;
            gap: 12px;
            flex-shrink: 0;
        }}

        .btn {{
            padding: 12px 24px;
            border-radius: 24px;
            border: none;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.875rem;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.3s ease;
            white-space: nowrap;
        }}

        .btn-play {{
            background: #1ED760;
            color: #000000;
            min-width: 100px;
        }}

        .btn-play:hover {{
            background: #1fdf64;
            transform: scale(1.05);
            box-shadow: 0 8px 24px rgba(30, 215, 96, 0.4);
        }}

        .btn-play.playing {{
            background: #ffffff;
            color: #000000;
        }}

        .btn-youtube {{
            background: #FF0000;
            color: #ffffff;
            border: 1px solid rgba(255, 0, 0, 0.3);
        }}

        .btn-youtube:hover {{
            background: #CC0000;
            border-color: rgba(255, 0, 0, 0.5);
            transform: scale(1.05);
        }}

        .btn:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
            transform: none !important;
        }}

        .btn-youtube:disabled {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .btn-youtube:disabled:hover {{
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.1);
        }}

        /* プレイヤーコンテナ */
        .player-container {{
            width: 100%;
            margin-top: 16px;
            border-radius: 12px;
            overflow: hidden;
            display: none;
            animation: fadeIn 0.3s ease;
            position: relative;
        }}

        .player-container.active {{
            display: block;
        }}

        .close-button {{
            position: absolute;
            top: 8px;
            right: 8px;
            background: #FF0000;
            color: #ffffff;
            border: 2px solid #ffffff;
            border-radius: 50%;
            width: 36px;
            height: 36px;
            font-size: 24px;
            font-weight: bold;
            line-height: 1;
            cursor: pointer;
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
        }}

        .close-button:hover {{
            background: #CC0000;
            transform: scale(1.15);
            box-shadow: 0 4px 12px rgba(255, 0, 0, 0.6);
        }}

        .spotify-player iframe {{
            width: 100%;
            height: 152px;
            border: none;
            border-radius: 12px;
        }}

        .youtube-player iframe {{
            width: 100%;
            height: 350px;
            border: none;
        }}

        .btn-spotify {{
            background: #1ED760;
            color: #000000;
        }}

        .btn-spotify:hover {{
            background: #1fdf64;
            transform: scale(1.05);
            box-shadow: 0 8px 24px rgba(30, 215, 96, 0.4);
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        footer {{
            text-align: center;
            margin-top: 80px;
            color: rgba(255, 255, 255, 0.3);
            font-size: 0.875rem;
            font-weight: 300;
        }}

        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 2.5rem;
            }}

            .track-card {{
                flex-direction: column;
                padding: 20px;
                gap: 16px;
            }}

            .rank {{
                font-size: 1.5rem;
            }}

            .album-cover {{
                width: 120px;
                height: 120px;
            }}

            .track-info {{
                text-align: center;
                width: 100%;
            }}

            .track-meta {{
                justify-content: center;
                flex-wrap: wrap;
            }}

            .actions {{
                flex-direction: column;
                width: 100%;
            }}

            .btn {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{artist}</h1>
            <p class="subtitle">Top Tracks</p>
        </header>

        <div class="track-list">
"""

    for track in tracks_data:
        duration_min = track['duration_ms'] // 60000
        duration_sec = (track['duration_ms'] % 60000) // 1000

        spotify_button = f"""
            <a href="{track['spotify_url']}" target="_blank" class="btn btn-spotify">
                Spotify
            </a>
        """

        youtube_button = f"""
            <a href="https://www.youtube.com/watch?v={track['video_id']}" target="_blank" class="btn btn-youtube">
                YouTube
            </a>
        """ if track['video_id'] else """
            <button class="btn btn-youtube" disabled>
                YouTube N/A
            </button>
        """

        youtube_player = ""

        html += f"""
            <div class="track-card" style="animation-delay: {track['rank'] * 0.05}s">
                <div class="rank">{track['rank']}</div>
                <img src="{track['img']}" alt="{track['name']}" class="album-cover">
                <div class="track-info">
                    <div class="track-name">{track['name']}</div>
                    <div class="track-meta">
                        <span>{track['release_date']}</span>
                        <span>{duration_min}:{duration_sec:02d}</span>
                    </div>
                    <div class="popularity-container">
                        <div class="popularity-bar">
                            <div class="popularity-fill" style="width: {track['popularity']}%"></div>
                        </div>
                        <div class="popularity-value">{track['popularity']}</div>
                    </div>
                    {youtube_player}
                </div>
                <div class="actions">
                    {spotify_button}
                    {youtube_button}
                </div>
            </div>
"""

    html += """
        </div>

        <footer>
            <p>Powered by Spotify & YouTube API</p>
        </footer>
    </div>

    <script>
        let currentPlayer = null;

        function toggleYouTube(rank) {{
            const player = document.getElementById('youtube-player-' + rank);

            // 同じプレイヤーをクリックした場合は閉じる
            if (currentPlayer && currentPlayer === player) {{
                currentPlayer.classList.remove('active');
                currentPlayer = null;
                return;
            }}

            // 全てのプレイヤーを閉じる
            document.querySelectorAll('.player-container').forEach(p => {{
                p.classList.remove('active');
            }});

            // YouTubeプレイヤーを開く
            if (player) {{
                player.classList.add('active');
                currentPlayer = player;
            }}
        }}

        function closeYouTube(rank) {{
            const player = document.getElementById('youtube-player-' + rank);
            if (player) {{
                player.classList.remove('active');
                currentPlayer = null;
            }}
        }}

        // ページ読み込み時のアニメーション
        window.addEventListener('load', function() {{
            const fills = document.querySelectorAll('.popularity-fill');
            fills.forEach(fill => {{
                const width = fill.style.width;
                fill.style.width = '0%';
                setTimeout(() => {{
                    fill.style.width = width;
                }}, 100);
            }});
        }});
    </script>
</body>
</html>
"""
    return html


# メイン処理
artist = get_artist_name()

if not artist:
    print("アーティスト名が入力されませんでした")
    exit()

print(f"検索中: {artist}")

# Spotifyでアーティストを検索
result_search = spotify.search(q=artist, type="artist", market=None)
artist_id = result_search["artists"]["items"][0]["id"]

# トップトラックを取得
results = spotify.artist_top_tracks(artist_id, country='JP')

# YouTube API の初期化
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# トラック情報を整理
tracks_data = []
for i, track in enumerate(sorted(results['tracks'], key=lambda x: x['popularity'], reverse=True)[:10], 1):
    print(f"処理中 ({i}/10): {track['name']}")

    # YouTubeで検索
    search_query = f"{artist} {track['name']}"
    try:
        search_response = youtube.search().list(
            part='id,snippet',
            q=search_query,
            order='relevance',
            type='video',
            maxResults=1
        ).execute()

        if search_response['items']:
            video_id = search_response['items'][0]['id']['videoId']
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"  → YouTube: {video_id}")
        else:
            video_id = ""
            youtube_url = ""
            print(f"  → YouTube: 見つかりませんでした")
    except Exception as e:
        print(f"  → YouTube エラー: {e}")
        video_id = ""
        youtube_url = ""

    tracks_data.append({
        'rank': i,
        'name': track['name'],
        'release_date': track['album']['release_date'],
        'duration_ms': track['duration_ms'],
        'popularity': track['popularity'],
        'preview_url': track['preview_url'],
        'img': track['album']['images'][0]['url'],
        'youtube_url': youtube_url,
        'video_id': video_id,
        'spotify_url': track['external_urls']['spotify'],
        'spotify_track_id': track['id']
    })

# HTMLファイルを生成
script_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(script_dir, f"{artist}_tracks.html")

print(f"\nHTMLファイルを生成中...")
html_content = generate_html(artist, tracks_data)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"完了: {html_path}")

# ブラウザで開く
print("ブラウザで開いています...")
webbrowser.open(f'file://{html_path}')
