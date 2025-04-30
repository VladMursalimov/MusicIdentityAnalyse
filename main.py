import asyncio

from flask import Flask, request, jsonify, render_template, Response
import apirequests

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    """Отображает главную HTML страницу"""
    return render_template('index.html')


@app.route('/get-tracks', methods=['POST'])
async def get_tracks():
    """Обрабатывает POST-запрос с ID пользователя и возвращает треки"""
    try:
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Получаем случайные треки с текстами
        tracks = await (apirequests.get_random_tracks_with_lyrics(user_id))

        return jsonify({
            "tracks": [{"track": track, "artist": artist, "lyrics": lyrics} for track, artist, lyrics in tracks]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/analyze-tracks', methods=['POST'])
def analyze_tracks():
    """Анализирует полученные треки с streaming ответом"""
    try:
        tracks = request.json.get('tracks')
        if not tracks:
            return jsonify({"error": "Tracks data is required"}), 400

        # Преобразуем полученные треки в нужный формат
        tracks_data = [(t['track'], t['artist'], t['lyrics']) for t in tracks]

        # Возвращаем потоковый ответ
        return Response(apirequests.generate_analysis(tracks_data), mimetype='text/plain')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)