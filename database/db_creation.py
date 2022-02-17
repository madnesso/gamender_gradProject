import sqlite3

# Create Database
conn = sqlite3.connect('gamender.db')
c = conn.cursor()

# Create Users Table
c.execute(
    '''CREATE TABLE IF NOT EXISTS user(user_id integer PRIMARY KEY AUTOINCREMENT, '''
    '''username text, '''
    '''password text)'''
)

# Create Games Table
c.execute(
    '''CREATE TABLE IF NOT EXISTS game(game_id integer PRIMARY KEY AUTOINCREMENT, '''
    '''game_name text, '''
    '''score integer, '''
    '''genre_id integer, '''
    '''FOREIGN KEY (genre_id) REFERENCES genre(genre_id))'''
)


# Create Genres Table
c.execute(
    '''CREATE TABLE IF NOT EXISTS genre(genre_id integer PRIMARY KEY AUTOINCREMENT, '''
    '''genre_name text)'''
)

# Create Handler Table
c.execute(
    '''CREATE TABLE IF NOT EXISTS handler(handler_id integer PRIMARY KEY AUTOINCREMENT, '''
    '''name text)'''
)


# Create Tweets Table
c.execute(
    '''CREATE TABLE IF NOT EXISTS tweet(tweet_id integer PRIMARY KEY AUTOINCREMENT, '''
    '''tweet char(280), '''
    '''handler_id integer, '''
    '''FOREIGN KEY (handler_id) REFERENCES handler(handler_id))'''
)


# Create users_genres Table (Many-to-Many Relation)
c.execute(
    '''CREATE TABLE IF NOT EXISTS users_genres(user_id integer, '''
    '''genre_id integer, '''
    '''PRIMARY KEY (user_id, genre_id), '''
    '''FOREIGN KEY (user_id) REFERENCES user(user_id), '''
    '''FOREIGN KEY (genre_id) REFERENCES genre(genre_id))'''
)


# Create users_games Table (Many-to-Many Relation)
c.execute(
    '''CREATE TABLE IF NOT EXISTS users_games(user_id integer, '''
    '''game_id integer, '''
    '''PRIMARY KEY (user_id, game_id), '''
    '''FOREIGN KEY (user_id) REFERENCES user(user_id), '''
    '''FOREIGN KEY (game_id) REFERENCES game(game_id))'''
)


# Create users_handlers Table (Many-to-Many Relation)
c.execute(
    '''CREATE TABLE IF NOT EXISTS users_handlers(user_id integer, '''
    '''handler_id integer, '''
    '''PRIMARY KEY (user_id, handler_id), '''
    '''FOREIGN KEY (user_id) REFERENCES user(user_id), '''
    '''FOREIGN KEY (handler_id) REFERENCES handler(handler_id))'''
)


# Create handlers_games Table (Many-to-Many Relation)
c.execute(
    '''CREATE TABLE IF NOT EXISTS handlers_games(handler_id integer, '''
    '''game_id integer, '''
    '''PRIMARY KEY (handler_id, game_id), '''
    '''FOREIGN KEY (handler_id) REFERENCES handler(handler_id), '''
    '''FOREIGN KEY (game_id) REFERENCES game(game_id))'''
)


# Create games_genres Table (Many-to-Many Relation)
c.execute(
    '''CREATE TABLE IF NOT EXISTS games_genres(game_id integer, '''
    '''genre_id integer, '''
    '''PRIMARY KEY (game_id, genre_id), '''
    '''FOREIGN KEY (game_id) REFERENCES game(game_id), '''
    '''FOREIGN KEY (genre_id) REFERENCES genre(genre_id))'''
)
