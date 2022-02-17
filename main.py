from scrapper.scrap import scrap
import sqlite3
import pandas as pd
from Evaluate import predict
from collaboration.colab import colab

if __name__ == '__main__':
    con = sqlite3.connect("./database/gamender.db")
    Games = pd.read_sql_query("SELECT game_name FROM game", con)
    con.close()
    scrap(Games)
    predict(Games)
    colab()
