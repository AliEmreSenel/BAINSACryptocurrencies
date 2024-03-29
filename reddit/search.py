"""Reddit searcher for cryptocurrency posts using the Pushshift API."""
import pmaw
import sqlite3
import tqdm
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
reddit = pmaw.PushshiftAPI()

# Start time for the search in unix epoch time
start_epoch = 1609459200


# Open reddit SQLite database
conn = sqlite3.connect("reddit.db")
c = conn.cursor()

# Create a table for the posts if it doesn't exist
c.execute(
    """CREATE TABLE IF NOT EXISTS posts (
   id text NOT NULL PRIMARY KEY ON CONFLICT IGNORE,
   title text,
   author text,
   created_utc integer,
   subreddit text,
   score integer,
   num_comments integer,
   permalink text,
   url text,
   selftext text,
   over_18 integer,
   is_video integer,
   is_original_content integer,
   is_self integer,
   is_meta integer,
   is_crosspostable integer,
   is_reddit_media_domain integer,
   is_robot_indexable integer,
   is_gallery integer,
   processed integer,
   comments_processed integer
   )"""
)

log.info("Table created")


queries = [
    "crypto",
    "solana",
    "bitcoin",
    "etherium",
    "ripple",
    "dogecoin",
    "apecoin",
    "btc",
    "eth",
    "sol",
    "xrp",
    "doge",
    "ape",
]

subreddits = []

for query in queries:
    log.info(f"Searching for {query}")

    gen = reddit.search_submissions(
        q=query,
        subreddit=subreddits,
        limit=None,
        since=start_epoch,
        mem_safe=True,
        safe_exit=True,
	until=1667503930,
    )

    # Insert post IDs into database if they don't already exist
    # This is to prevent duplicate posts
    # Show progress using tqdm
    for postID in tqdm.tqdm([post["id"] for post in gen]):
        c.execute("INSERT OR IGNORE INTO posts (id) VALUES (?)", (postID,))
        conn.commit()

conn.close()
