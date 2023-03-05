"""Reddit Post and Comment Data Scraper.

Run search.py first to get post ids
Before running the script, make sure to get client id and secret from reddit and add to secrets.json using the following format:
{"client_id": "", "client_secret": ""}
"""
import praw
import prawcore
import tqdm
import sqlite3
import json
from tqdm.contrib.concurrent import process_map  # or thread_map


# Connect to the database
conn = sqlite3.connect("reddit.db")
c = conn.cursor()

# Create the tables for posts and comments
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

c.execute(
    """CREATE TABLE IF NOT EXISTS comments
               (id text PRIMARY KEY,
                parent_id text,
                link_id text,
                subreddit text,
                author text,
                body text,
                score int,
                created_utc int)
            """
)

# Commit the changes
conn.commit()

print("Created tables")

with open("secrets.json", "r") as f:
    secrets = json.load(f)
    reddit = praw.Reddit(
        client_id=secrets["client_id"],
        client_secret=secrets["client_secret"],
        user_agent="BAINSA Reddit Scraper",
    )

    postList = []

    # Get posts that have not been processed
    c.execute("SELECT * FROM posts WHERE processed is NULL")

    print("Getting posts")

    for row in tqdm.tqdm(c.fetchall()):
        postList.append(row[0])

    def process_post(post):
        """Download up-to-date post data and comments from Reddit.

        :param post: post ID
        :returns: None

        """
        try:
            submission = reddit.submission(id=post)

            # Update the post data
            # Do some processing on the data to convert praw objects to strings
            # Also convert booleans to integers
            c.execute(
                "UPDATE posts SET title = ?, author = ?, created_utc = ?, subreddit = ?, score = ?, num_comments = ?, permalink = ?, url = ?, selftext = ?, over_18 = ?, is_video = ?, is_original_content = ?, is_self = ?, is_meta = ?, is_crosspostable = ?, is_reddit_media_domain = ?, is_robot_indexable = ?, is_gallery = ?, processed = 1 WHERE id = ?",
                (
                    str(submission.title),
                    str(submission.author),
                    int(submission.created_utc),
                    str(submission.subreddit),
                    int(submission.score),
                    int(submission.num_comments),
                    str(submission.permalink),
                    str(submission.url),
                    str(submission.selftext),
                    int(submission.over_18),
                    int(submission.is_video),
                    int(submission.is_original_content),
                    int(submission.is_self),
                    int(submission.is_meta),
                    int(submission.is_crosspostable),
                    int(submission.is_reddit_media_domain),
                    int(submission.is_robot_indexable),
                    int(submission.is_gallery)
                    if hasattr(submission, "is_gallery")
                    else 0,
                    post,
                ),
            )

            submission.comments.replace_more(limit=None)
            if len(submission.comments) > 0:
                for comment in submission.comments.list():
                    c.execute(
                        "INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            comment.id,
                            comment.parent_id,
                            comment.link_id,
                            str(comment.subreddit),
                            str(comment.author),
                            comment.body,
                            comment.score,
                            comment.created_utc,
                        ),
                    )
            c.execute("UPDATE posts SET comments_processed = 1 WHERE id = ?", (post,))

            # Commit the changes to the database
            # conn.commit()
        except prawcore.exceptions.ResponseException:
            tqdm.tqdm.write(
                f"Error with post {post} (Post / Comment might be deleted or banned)"
            )
            try:
                c.execute("UPDATE posts SET processed = 0 WHERE id = ?", (post,))
                conn.commit()
            except sqlite3.OperationalError:
                pass
        except Exception as e:
            tqdm.tqdm.write(f"Error with post {post}: {e}")
        # Close the connection

    process_map(process_post, postList, max_workers=1, chunksize=1)
conn.commit()
conn.close()
