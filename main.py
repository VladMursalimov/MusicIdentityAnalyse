from flask import Flask, request, jsonify, render_template
import apirequests

app = Flask(__name__)

@app.route('/')
def index():
    """Отображает главную HTML страницу"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Обрабатывает POST-запрос с ID пользователя и возвращает анализ"""
    try:
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Получаем случайные треки с текстами
        tracks = apirequests.get_random_tracks_with_lyrics(user_id)

        # Анализируем треки
        analysis = apirequests.analyze_tracks(tracks)

        return jsonify({
            "tracks": [{"track": track, "artist": artist, "lyrics": lyrics} for track, artist, lyrics in tracks],
            "analysis": analysis
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)