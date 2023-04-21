"""searchAlt.py - Search for posts with specific keywords and add them to the database."""
import zstandard as zstd
import json
import requests
import logging
import tqdm
from tqdm.contrib.concurrent import process_map
import mysql.connector
import sys
from io import BytesIO, SEEK_SET, SEEK_END

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

postBar = tqdm.tqdm(position=6, total=2 * 12 * 10**6, unit="posts")


year = int(sys.argv[1])
monthStart = int(sys.argv[2])
monthEnd = int(sys.argv[3])


def processPosts(month):
    """Process posts for a given month."""
    tconn = mysql.connector.connect(
        host="localhost", user="reddit", password="red.dit+bot", database="bainsa"
    )
    tc = tconn.cursor()
    r = requests.get(
        f"https://files.pushshift.io/reddit/submissions/RS_{year}-{month:02}.zst",
        stream=True,
    )
    stream = ResponseStream(r, month - monthStart, r.iter_content(2**12))
    dctx = zstd.ZstdDecompressor(max_window_size=2147483648)
    with dctx.stream_reader(stream) as reader:
        previous_line = ""
        while True:
            chunk = reader.read(2**24)  # 16mb chunks
            if not chunk:
                break

            string_data = chunk.decode("utf-8")
            lines = string_data.split("\n")
            for i, line in enumerate(lines[:-1]):
                if i == 0:
                    line = previous_line + line
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
                    tc.execute(
                        "INSERT IGNORE INTO posts (id) VALUES (%s)",
                        (postID,),
                    )
                    tconn.commit()
                # do something with the object here
            previous_line = lines[-1]
    tconn.close()


process_map(
    processPosts,
    range(
        monthStart,
        monthEnd + 1,
    ),
    max_workers=4,
    chunksize=1,
    position=1,
    leave=False,
)


class ResponseStream(object):
    """A file-like object that reads from a requests response iterator."""

    def __init__(self, r, i, request_iterator):
        """Initialize the stream.

        :param r: The requests response object.
        :param i: The index of the thread.
        :param request_iterator: The iterator returned by r.iter_content().
        """
        self._bytes = BytesIO()
        self._iterator = request_iterator
        self.pbar = tqdm.tqdm(
            total=int(r.headers.get("content-length", 0)),
            unit="B",
            unit_scale=True,
            position=2 + i,
        )

    def _load_all(self):
        self._bytes.seek(0, SEEK_END)
        for chunk in self._iterator:
            self._bytes.write(chunk)

    def _load_until(self, goal_position):
        current_position = self._bytes.seek(0, SEEK_END)
        while current_position < goal_position:
            try:
                current_position += self._bytes.write(next(self._iterator))
                self.pbar.n = current_position
                self.pbar.refresh()
            except StopIteration:
                break

    def tell(self):
        """Return the current position of the stream."""
        return self._bytes.tell()

    def read(self, size=None):
        """Read from the stream.

        :param size: The number of bytes to read. If None, read all bytes.
        """
        left_off_at = self._bytes.tell()
        if size is None:
            self._load_all()
        else:
            goal_position = left_off_at + size
            self._load_until(goal_position)

        self._bytes.seek(left_off_at)
        return self._bytes.read(size)

    def seek(self, position, whence=SEEK_SET):
        """Seek to a position in the stream.

        :param position: The position to seek to.
        :param whence: The reference point for the position. Defaults to SEEK_SET.
        """
        if whence == SEEK_END:
            self._load_all()
        else:
            self._bytes.seek(position, whence)
