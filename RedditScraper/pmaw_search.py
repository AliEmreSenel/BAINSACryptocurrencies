import json
import pmaw
import sqlite3
import tqdm

reddit = pmaw.PushshiftAPI()
start_epoch = 1609459200


# Open reddit sqlite database
conn = sqlite3.connect("reddit.db")

# Create a cursor
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
   processed boolean,
   comments_processed boolean
   )"""
)

print("Table created successfully")

count = 0


def filter(item):
    global count
    count += 1
    if count % 200 == 0:
        print(count)

    return True


queries = [
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
    print(f"Querying {query}")
    gen = reddit.search_submissions(
        q=query,
        subreddit=subreddits,
        limit=None,
        since=start_epoch,
        mem_safe=True,
        safe_exit=True,
        filter_fn=filter,
    )
    # Insert post IDs into database if they don't already exist
    # This is to prevent duplicate posts
    # Show progress using tqdm
    for postID in tqdm.tqdm([post["id"] for post in gen]):
        c.execute("INSERT OR IGNORE INTO posts (id) VALUES (?)", (postID,))
        conn.commit()
conn.close()
