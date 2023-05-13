"""searchAlt.py - Search for posts with specific keywords and add them to the database."""
import zstandard as zstd
import json
import logging
import tqdm
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost", user="reddit", password="red.dit+bot", database="bainsa"
)


logging.basicConfig(level=logging.DEBUG)

# Create a table for the posts if it doesn't exist

c = mydb.cursor()

c.execute(
    """CREATE TABLE IF NOT EXISTS posts (
   id varchar(20) NOT NULL PRIMARY KEY,
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

# log.info("Table created")

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


def processPosts():
    """Process posts for a given month."""
    tconn = mysql.connector.connect(
        host="localhost", user="reddit", password="red.dit+bot", database="bainsa"
    )
    tc = tconn.cursor(prepared=True)
    postBar = tqdm.tqdm(
        position=6, total=30 * 10**4, unit="posts"
    )
    file = open("/mnt/disk3/reddit/submissions/RS_2022-10.zst", "rb")
    dctx = zstd.ZstdDecompressor(max_window_size=2147483648)
    with dctx.stream_reader(file) as reader:
        previous_line = ""
        while True:
            chunk = reader.read(2**24)  # 16mb chunks
            if not chunk:
                break

            try:
                string_data = chunk.decode("utf-8")
            except Exception:
                continue
            lines = string_data.split("\n")
            for i, line in enumerate(lines[:-1]):
                if i == 0:
                    line = previous_line + line
                try:
                    object = json.loads(line)
                    if any(
                        any(
                            [
                                query in object["title"].lower().split(" "),
                                query in object["selftext"].lower().split(" "),
                            ]
                        )
                        for query in queries
                    ):
                        postBar.update(1)
                        postID = object["id"]
                        tc.execute("INSERT IGNORE INTO posts (id) VALUES (%s)", (postID,),)
                except Exception:
                    continue
                # do something with the object here
            previous_line = lines[-1]
            tconn.commit()
    tconn.close()


processPosts()
