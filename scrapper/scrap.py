import hashlib
import json
import datetime
from scrapper import utils


def search(db_path, q, auth, **kwargs):
    """
    Save tweets from a search. Full documentation here:

    https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets
    """
    stop_after = kwargs.pop("stop_after", None)
    auth = json.load(open(auth))
    session = utils.session_for_auth(auth)
    db = utils.open_database(db_path)

    search_args = {"q": q}
    for key, value in kwargs.items():
        if value is not None:
            search_args[key] = value

    args_hash = hashlib.sha1(
        json.dumps(search_args, sort_keys=True, separators=(",", ":")).encode("utf8")
    ).hexdigest()

    tweets = utils.fetch_timeline(
        session,
        "https://api.twitter.com/1.1/search/tweets.json",
        db,
        search_args,
        sleep=6,
        key="statuses",
        stop_after=stop_after,
        since_type="search",
        since_key=args_hash,
    )
    print("Start scrapping game: " + q)
    chunk = []
    first = True

    if not db["search_runs"].exists():
        db["search_runs"].create(
            {"id": int, "name": str, "args": str, "started": str, "hash": str}, pk="id"
        )

    def save_chunk(db, search_run_id, chunk):
        utils.save_tweets(db, chunk)
        # Record which search run produced them
        db["search_runs_tweets"].insert_all(
            [{"search_run": search_run_id, "tweet": tweet["id"]} for tweet in chunk],
            pk=("search_run", "tweet"),
            foreign_keys=(
                ("search_run", "search_runs", "id"),
                ("tweet", "tweets", "id"),
            ),
            replace=True,
        )

    search_run_id = None
    for tweet in tweets:
        if first:
            first = False
            search_run_id = (
                db["search_runs"].insert(
                    {
                        "name": search_args["q"],
                        "args": {
                            key: value
                            for key, value in search_args.items()
                            if key not in {"q", "count"}
                        },
                        "started": datetime.datetime.utcnow().isoformat(),
                        "hash": args_hash,
                    },
                    alter=True,
                ).last_pk
            )
        chunk.append(tweet)
        if len(chunk) >= 10:
            save_chunk(db, search_run_id, chunk)
            chunk = []
    if chunk:
        save_chunk(db, search_run_id, chunk)


def scrap(games):
    for i in games['game_name']:
        search(db_path="C:/Users/beel/gamender/data" + i, q=i, auth="C:/Users/beel/gamender/scrapper/auth.json")
