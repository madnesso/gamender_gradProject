import pandas as pd
import sqlite3
import re
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from database.games import add_game_score
from database.handlers import add_handler, add_liked_games

tokenizer = AutoTokenizer.from_pretrained("./models/trial5")
model = AutoModelForSequenceClassification.from_pretrained("./models/trial5")
hashtags = re.compile(r"^#\S+|\s#\S+")
mentions = re.compile(r"^@\S+|\s@\S+")
urls = re.compile(r"https?://\S+")


def process_text(text):
    text = re.sub(r'http\S+', '', text)
    text = hashtags.sub(' hashtag', text)
    text = mentions.sub(' entity', text)
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())


def predictionPipeline(text):
    # id_tolabel = {0: "Negative", 2: "Positive"}
    modeleval = model.eval()
    tokenized = tokenizer(text, return_tensors='pt', truncation=True).to(modeleval.device)
    with torch.no_grad(): label = torch.argmax(model.forward(**tokenized).logits, dim=1)[0].cuda().item()
    return label


def predict(games):
    # Read sqlite query results into a pandas DataFrame
    for i in games['game_name']:
        con = sqlite3.connect("./data/" + i)
        df = pd.read_sql_query("SELECT user, full_text FROM tweets", con)
        con.close()

        df["Test"] = df.full_text.apply(process_text)
        df.drop(columns='full_text', inplace=True)

        df['Test'].replace('', np.nan, inplace=True)
        df.dropna(subset=['Test'], inplace=True)

        print("Starting prediction for " + i)
        df['prediction'] = df['Test'].apply(predictionPipeline)
        df_positive = df[df['prediction'] == 2]
        print("done now adding handlers and " + i + " to their liked games ")
        for j in df_positive['user']:
            add_handler(int(j))
            add_liked_games(int(j), i)
        print("done now adding the score score")
        score = df[df["prediction"] == 2].count()[0] / (
                df[df["prediction"] == 2].count()[0] + df[df["prediction"] == 0].count()[0]) * 100
        score = int(score)
        add_game_score(i, score)
