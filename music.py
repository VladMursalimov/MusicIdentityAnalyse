from yandex_music import Client

def getUserLikedTracks(user_id):
    """Возвращает список всех любимых треков пользователя в формате [(трек, исполнитель), ...]"""
    client = Client().init()
    playlist = client.users_playlists("3", user_id)  # "3" — это идентификатор плейлиста "Мне нравится"
    tracks = playlist.fetchTracks()

    liked_tracks = []

    for track in tracks:
        try:
            track_title = track.track.title
            artist_name = track.track.artists[0].name
            liked_tracks.append((track_title, artist_name))
        except (AttributeError, IndexError):
            continue

    return liked_tracks

