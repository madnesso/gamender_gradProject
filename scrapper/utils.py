import re
import time
import html
import sqlite_utils
from requests_oauthlib import OAuth1Session
import datetime

SINCE_ID_TYPES = {
    "user": 1,
    "home": 2,
    "mentions": 3,
    "search": 4,
}
COUNT_HISTORY_TYPES = {
    "followers": 1,
    "friends": 2,
    "listed": 3,
    # Don't track these - they're uninteresting and really noisy in terms
    # of writing new rows to the count_history table:
    # "favourites": 4,
    # "statuses": 5,
}
source_re = re.compile('<a href="(?P<url>.*?)".*?>(?P<name>.*?)</a>')


def session_for_auth(auth):
    return OAuth1Session(
        client_key=auth["api_key"],
        client_secret=auth["api_secret_key"],
        resource_owner_key=auth["access_token"],
        resource_owner_secret=auth["access_token_secret"],
    )


def open_database(db_path):
    db = sqlite_utils.Database(db_path)
    if db.tables:
        migrate(db)
    return db


def migrate(db):
    from scrapper.migration import MIGRATIONS

    if "migrations" not in db.table_names():
        db["migrations"].create({"name": str, "applied": str}, pk="name")
    applied_migrations = {
        m[0] for m in db.conn.execute("select name from migrations").fetchall()
    }
    for migration in MIGRATIONS:
        name = migration.__name__
        if name in applied_migrations:
            continue
        migration(db)
        db["migrations"].insert(
            {"name": name, "applied": datetime.datetime.utcnow().isoformat()}
        )


def fetch_timeline(
        session,
        url,
        db,
        args=None,
        sleep=1,
        stop_after=None,
        key=None,
        since_type=None,
        since_key=None,
):
    # See https://developer.twitter.com/en/docs/tweets/timelines/guides/working-with-timelines
    since_type_id = None
    last_since_id = None
    if since_type is not None:
        assert since_key is not None
        since_type_id = SINCE_ID_TYPES[since_type]
    args = dict(args or {})
    args["count"] = 200
    if stop_after is not None:
        args["count"] = stop_after
    args["tweet_mode"] = "extended"
    min_seen_id = None
    num_rate_limit_errors = 0
    T = 0
    while True:
        T = T + 1
        if min_seen_id is not None:
            args["max_id"] = min_seen_id - 1
        response = session.get(url, params=args)
        tweets = response.json()
        print("run " + str(T))
        if "errors" in tweets:
            print(tweets["errors"][0]["code"])
            # Was it a rate limit error? If so sleep and try again
            if 88 == tweets["errors"][0]["code"]:
                num_rate_limit_errors += 1
                assert num_rate_limit_errors < 5, "More than 5 rate limit errors"
                print(
                    "Rate limit exceeded - will sleep 15s and try again {}".format(
                        repr(response.headers)
                    )
                )
                time.sleep(15)
                continue
            else:
                raise Exception(str(tweets["errors"]))
        if key is not None:
            tweets = tweets[key]
        if not tweets:
            break
        for tweet in tweets:
            yield tweet
        min_seen_id = min(t["id"] for t in tweets)
        max_seen_id = max(t["id"] for t in tweets)
        if last_since_id is not None:
            max_seen_id = max((last_since_id, max_seen_id))
            last_since_id = max_seen_id
        if since_type_id is not None and since_key is not None:
            db["since_ids"].insert(
                {
                    "type": since_type_id,
                    "key": since_key,
                    "since_id": max_seen_id,
                },
                replace=True
            )
        time.sleep(sleep)
        if T == 3:
            break


def ensure_tables(db):
    table_names = set(db.table_names())
    if "tweets" not in table_names:
        db["tweets"].create(
            {
                "id": int,
                "user": int,
                "full_text": str,
            },
            pk="id"
        )
        db["tweets"].enable_fts(["full_text"], create_triggers=True)


def expand_entities(s, entities):
    for _, ents in entities.items():
        for ent in ents:
            if "url" in ent:
                replacement = ent["expanded_url"] or ent["url"]
                s = s.replace(ent["url"], replacement)
    return s


def transform_tweet(tweet):
    tweet["full_text"] = html.unescape(
        expand_entities(tweet["full_text"], tweet.pop("entities"))
    )


def save_tweets(db, tweets):
    ensure_tables(db)
    for tweet in tweets:
        transform_tweet(tweet)
        user = tweet.pop("user")
        tweet["user"] = user["id"]
        tweet.pop("extended_entities", None)
        # Deal with nested retweeted_status / quoted_status
        nested = []
        for tweet_key in ("quoted_status", "retweeted_status"):
            if tweet.get(tweet_key):
                nested.append(tweet[tweet_key])
                tweet[tweet_key] = tweet[tweet_key]["id"]
        if nested:
            save_tweets(db, nested)
        db["tweets"].insert(tweet, pk="id", alter=True, replace=True)


def extract_and_save_source(db, source):
    if not source:
        return None
    m = source_re.match(source)
    details = m.groupdict()
    return db["sources"].insert(details, hash_id="id", replace=True).last_pk
