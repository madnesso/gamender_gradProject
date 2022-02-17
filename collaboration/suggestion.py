import sqlite3
import pandas as pd
import numpy as np
from collections import Counter
from itertools import chain

conn = sqlite3.connect('../database/gamender.db')
c = conn.cursor()
data_neighbours = pd.read_sql_query("SELECT * FROM collaboration", conn, index_col='game_id')


def remove_alrdy_played(a, b):
    for i in a[:]:
        if i in b:
            a.remove(i)


def gettopgame(l):
    common = []
    listoflists = []
    if len(l) == 1:
        common.append(data_neighbours.iloc[l[0] - 1, 0])
        return common
    else:
        n = len(l)
        for j in range(0, n):
            listoflists.append(list(data_neighbours.iloc[l[j] - 1]))
        common = list(chain.from_iterable(listoflists))
        commonofmany = [k for k, v in Counter(common).items() if v > 1]
        if len(commonofmany) > 0:
            remove_alrdy_played(commonofmany, l)
            return commonofmany
        else:
            remove_alrdy_played(common, l)
            return list(dict.fromkeys(common))
