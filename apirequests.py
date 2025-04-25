import os
import random
from openai import OpenAI
from music import getUserLikedTracks
import lyricsgenius
from dotenv import load_dotenv
import re

load_dotenv()

genius = lyricsgenius.Genius(os.getenv("GENIUS_TOKEN"))
openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("APIKEY"),
)

def get_random_tracks_with_lyrics(user_id, count=15):
    """Возвращает 10 случайных треков с текстами (если найдены)."""
    liked_tracks = getUserLikedTracks(user_id)
    random.shuffle(liked_tracks)  # Перемешиваем треки
    selected_tracks = liked_tracks[:count]

    tracks_with_lyrics = []
    for track, artist in selected_tracks:
        try:
            song = genius.search_song(track, artist)
            lyrics = song.lyrics if song else "Текст не найден"
            tracks_with_lyrics.append((track, artist, lyrics))
        except Exception as e:
            print(f"Ошибка при поиске текста для {track}: {e}")
            tracks_with_lyrics.append((track, artist, "Текст не найден"))

    return tracks_with_lyrics

def analyze_tracks(tracks):
    """Отправляет треки и тексты в OpenAI для анализа."""
    tracks_str = "\n\n".join(
        f"🎵 {track} — {artist}\nТекст:\n{lyrics}"
        for track, artist, lyrics in tracks
    )

    response = openai_client.chat.completions.create(
        model="qwen/qwq-32b:free",
        messages=[
            {
                "role": "system",
                "content": "Ты — музыкальный психолог. "
                           "Проанализируй личность человека на основе его любимых треков и их текстов."
            },
            {
                "role": "user",
                "content": (
                    "Вот 10 моих любимых треков с текстами:\n\n"
                    f"{tracks_str}\n\n"
                    "Напиши развёрнутый анализ (5-7 предложений). "
                    "Учитывай эмоции, темы, стиль музыки и слова. "
                    "Отвечай только на русском языке."
                )
            }
        ]
    )

    # Получаем сырой текст анализа
    raw_analysis = response.choices[0].message.content.strip()

    # Разделяем текст на абзацы по двум переносам строки (\n\n)
    paragraphs = re.split(r'\n\s*\n', raw_analysis)

    # Возвращаем список абзацев
    return paragraphs