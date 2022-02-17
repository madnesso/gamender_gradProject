import pandas as pd
import sqlite3
import numpy as np
from scipy.spatial.distance import cosine


def sublist_uniques(data, sublist):
    categories = set()
    for d, t in data.iterrows():
        try:
            for j in t[sublist]:
                categories.add(j)
        except:
            pass
    return list(categories)


def sublists_to_dummies(f, sublist, index_key=None):
    categories = sublist_uniques(f, sublist)
    frame = pd.DataFrame(columns=categories)
    for d, i in f.iterrows():
        if type(i[sublist]) == list or np.array:
            try:
                if index_key is not None:
                    key = i[index_key]
                    f = np.zeros(len(categories))
                    for j in i[sublist]:
                        f[categories.index(j)] = 1
                    if key in frame.index:
                        for j in i[sublist]:
                            frame.loc[key][j] += 1
                    else:
                        frame.loc[key] = f
                else:
                    f = np.zeros(len(categories))
                    for j in i[sublist]:
                        f[categories.index(j)] = 1
                    frame.loc[d] = f
            except:
                pass

    return frame


def ibs_fill(data_ibs, data):
    for i in range(0, len(data_ibs.columns)):
        for j in range(0, len(data_ibs.columns)):
            data_ibs.iloc[i, j] = 1 - cosine(data.iloc[:, i], data.iloc[:, j])
    return data_ibs


def get_top_n(data_ibss, n):
    data_neighbourss = pd.DataFrame(index=data_ibss.columns, columns=range(1, n + 1))
    for i in range(0, len(data_ibss.columns)):
        data_neighbourss.iloc[i, :n] = data_ibss.iloc[:, i].sort_values(ascending=False)[:n].index
    return data_neighbourss


def colab():
    print("Start Colab")
    con = sqlite3.connect("C:/Users/beel/gamender/database/gamender.db")
    df = pd.read_sql_query("SELECT handler_id, game_id  FROM handlers_games", con)

    con.close()
    df.set_index('handler_id')
    df.reset_index(inplace=True)
    gb = df.groupby(['handler_id'])
    result = gb['game_id'].unique()
    resultframe = result.to_frame()
    sparseframe = sublists_to_dummies(resultframe, 'game_id')
    sparseframe.index.name = 'handler_id'
    data = sparseframe.reset_index()
    data = data.drop('handler_id', 1)
    data_ibs = pd.DataFrame(index=data.columns, columns=data.columns)
    data_ibs = ibs_fill(data_ibs, data)
    data_neighbours = get_top_n(data_ibs, 5)
    data_neighbours.index.name = 'game_id'
    data_neighbours.rename(columns={data_neighbours.columns[0]: 'sim1'}, inplace=True)
    data_neighbours.rename(columns={data_neighbours.columns[1]: 'sim2'}, inplace=True)
    data_neighbours.rename(columns={data_neighbours.columns[2]: 'sim3'}, inplace=True)
    data_neighbours.rename(columns={data_neighbours.columns[3]: 'sim4'}, inplace=True)
    data_neighbours.rename(columns={data_neighbours.columns[4]: 'sim5'}, inplace=True)
    print('done, result game to game relation: ')
    print(data_neighbours.head())
    conn = sqlite3.connect('C:/Users/beel/gamender/database/gamender.db')
    data_neighbours.to_sql('collaboration', conn, if_exists='replace', index=True)
    conn.close()
