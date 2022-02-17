import sqlite3

conn = sqlite3.connect('gamender.db')
c = conn.cursor()


# User Makes an Account (Register)
def add_user(name, password):
    user = (name, password)
    c.execute('SELECT username FROM users WHERE username = ?', (name,))
    if not c.fetchone():
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', user)
    else:
        print("Username already exists")
    conn.commit()


def login(name, password):
    user = (name, password)
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', user)
    if not c.fetchone():
        print("Username and password do not match")
    else:
        print("Welcome back!")
    conn.commit()


def delete_user(u_id):
    c.execute('DELETE FROM users WHERE user_id = ?', (u_id,))
    conn.commit()


def change_username(u_id, name):
    user = (name, u_id)
    c.execute('SELECT username FROM users WHERE username = ?', (name,))
    if not c.fetchone():
        c.execute('UPDATE users SET username = ? WHERE user_id = ?', user)
    else:
        print("Username already exists")
    conn.commit()


# Return All the Games Liked by a User
def get_user_games(u_id):
    c.execute('SELECT game_id FROM users_games WHERE user_id = ?', (u_id,))
    games = c.fetchall()
    return games


# User Adds their Favourite Genres
def add_genre(genre_name, u_id):
    c.execute('SELECT genre_id FROM genre WHERE genre_name = ?', (genre_name,))
    genre_id = c.fetchone()
    c.execute('SELECT * FROM genre WHERE user_id = ? AND genre_id = ?', (u_id, genre_id))
    if not c.fetchone():
        c.execute('INSERT INTO users_genres (user_id, genre_id) VALUES (?, ?)', (u_id, genre_id))
    conn.commit()


# Remove a Genre from the User's Favourite Genres
def delete_genres(genre_name, u_id):
    c.execute('SELECT genre_id FROM genre WHERE genre_name = ?', (genre_name,))
    genre_id = c.fetchone()
    c.execute('DELETE FROM users_genres WHERE u_id = ? AND genre_id = ?', (u_id, genre_id))
    conn.commit()


# Add User to Handlers Table
def add_user_to_handlers(u_id):
    c.execute('SELECT username FROM user WHERE user_id = ?', (u_id,))
    name = c.fetchone()
    c.execute('SELECT name FROM handler WHERE name = ?', (name,))
    if not c.fetchone():
        c.execute('INSERT INTO handler (name) VALUES (?)', (name,))
    conn.commit()
