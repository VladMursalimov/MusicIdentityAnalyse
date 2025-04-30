import asyncio
import os
import random
from openai import OpenAI
from default.music import getUserLikedTracks
import lyricsgenius
from dotenv import load_dotenv
import re

load_dotenv()

genius = lyricsgenius.Genius(os.getenv("GENIUS_TOKEN"))
openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("APIKEY"),
)


async def fetch_lyrics(track, artist):
    """Асинхронно получает текст песни для одного трека."""
    try:
        # Запускаем синхронный код в отдельном потоке
        song = await asyncio.to_thread(genius.search_song, track, artist)
        return (track, artist, song.lyrics if song else "Текст не найден")
    except Exception as e:
        print(f"Ошибка при поиске текста для {track}: {e}")
        return (track, artist, "Текст не найден")


async def get_random_tracks_with_lyrics(user_id, count=15):
    """Асинхронно возвращает случайные треки с текстами."""
    liked_tracks = getUserLikedTracks(user_id)
    random.shuffle(liked_tracks)
    selected_tracks = liked_tracks[:count]

    tasks = [fetch_lyrics(track, artist) for track, artist in selected_tracks]
    tracks_with_lyrics = await asyncio.gather(*tasks)

    return tracks_with_lyrics

def analyze_tracks(tracks):
    """Отправляет треки и тексты в OpenAI для анализа."""
    tracks_str = "\n\n".join(
        f"🎵 {track} — {artist}\nТекст:\n{lyrics}"
        for track, artist, lyrics in tracks
    )

    response = openai_client.chat.completions.create(
        model="meta-llama/llama-4-scout:free",
        messages=[
            {
                "role": "system",
                "content": "Ты — музыкальный психолог. "
                           "Проанализируй личность человека на основе его любимых треков и их текстов."
            },
            {
                "role": "user",
                "content": (
                    "Вот некоторые мои любимые треки с текстами:\n\n"
                    f"{tracks_str}\n\n"
                    "Напиши развёрнутый анализ (3-5 предложений). "
                    "Учитывай эмоции, темы, стиль музыки и слова. "
                    "Отвечай только на русском языке."
                )
            }
        ]
    )

    print(response)

    # Получаем сырой текст анализа
    raw_analysis = response.choices[0].message.content.strip()

    # Разделяем текст на абзацы по двум переносам строки (\n\n)
    paragraphs = re.split(r'\n\s*\n', raw_analysis)

    # Возвращаем список абзацев
    return paragraphs


def generate_analysis(tracks_data):
    """
    Генерирует потоковый анализ треков через OpenAI API
    :param tracks_data: Список кортежей (трек, артист, текст)
    :return: Генератор текста анализа
    """
    stream = openai_client.chat.completions.create(
        model="tngtech/deepseek-r1t-chimera:free",
        messages=[
            {
                "role": "user",
                "content": "Ты — музыкальный психолог. "
                          "Проанализируй мою личность на основе моих любимых треков и их текстов."
            },
            {
                "role": "user",
                "content": (
                    "Вот некоторые мои любимые треки с текстами:\n\n" +
                    "\n\n".join(
                        f"🎵 {track} — {artist}\nТекст:\n{lyrics}"
                        for track, artist, lyrics in tracks_data
                    ) +
                    "\n\nНапиши развёрнутый анализ (5-7 предложений)."
                    "Если сможешь - то поищи информацию в интернете по этим трекам."
                    "Учитывай эмоции, темы, стиль музыки и слова."
                    "Отвечай только на русском языке."
                )
            }
        ],
        stream=True
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content