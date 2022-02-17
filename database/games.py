import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "gamender.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()


def get_game_genre(game_id):
    c.execute('SELECT genre_id FROM game WHERE game_id = ?', (game_id,))
    genre_id = c.fetchone()
    genre_id = genre_id[0]
    return genre_id


def get_game_name(game_id):
    c.execute('SELECT game_name FROM game WHERE game_id = ?', (game_id,))
    game_name = c.fetchone()
    game_name = game_name[0]
    return game_name


def get_game_id(game_name):
    c.execute('SELECT game_id FROM game WHERE game_name = ?', (game_name,))
    game_id = c.fetchone()
    game_id = game_id[0]
    return game_id


def get_games_by_genre(genre_id):
    c.execute('SELECT game_id FROM games_genres WHERE genre_id = ?', (genre_id,))
    games = c.fetchall()
    return games


def add_game_score(game_name, score):
    c.execute('SELECT game_id FROM game WHERE game_name = ?', (game_name,))
    game_id = c.fetchone()
    game_id = game_id[0]
    print(game_id)
    c.execute('UPDATE game SET score = ? WHERE game_id = ?', (score, game_id))
    conn.commit()
    print(game_name + " " + str(score) + " done")
