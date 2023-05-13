"""Reddit Post and Comment Data Scraper. Uses MYSQL database instead of SQLite.

Run search.py first to get post ids
Before running the script, make sure to get client id and secret from reddit and add to secrets.json using the following format:
{"client_id": "", "client_secret": ""}
"""
import praw
import prawcore
import tqdm
import json
from tqdm.contrib.concurrent import thread_map
import mysql.connector

conn = mysql.connector.connect(
    host="localhost", user="reddit", password="red.dit+bot", database="bainsa"
)

# Connect to the database
c = conn.cursor()

# Create the tables for posts and comments
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

c.execute(
    """CREATE TABLE IF NOT EXISTS comments
               (id varchar(20) PRIMARY KEY,
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

    def process_post(tc, submission):
        post = submission.id
        tc.execute(
            "UPDATE posts SET title = %s, author = %s, created_utc = %s, subreddit = %s, score = %s, num_comments = %s, permalink = %s, url = %s, selftext = %s, over_18 = %s, is_video = %s, is_original_content = %s, is_self = %s, is_meta = %s, is_crosspostable = %s, is_reddit_media_domain = %s, is_robot_indexable = %s, is_gallery = %s, processed = 1 WHERE id = %s",
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
            tc.executemany(
                "INSERT INTO comments VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    (
                        str(comment.id),
                        str(comment.parent_id),
                        str(comment.link_id),
                        str(comment.subreddit),
                        str(comment.author),
                        str(comment.body),
                        int(comment.score),
                        int(comment.created_utc),
                    )
                    for comment in submission.comments.list()
                ],
            )
        tc.execute(
            "UPDATE posts SET comments_processed = 1 WHERE id = %s", (post,),
        )


    def process_posts(posts):
        """Download up-to-date post data and comments from Reddit.

        :param posts: batch of 100 post ids
        :returns: None

        """
        tconn = mysql.connector.connect(
            host="localhost", user="reddit", password="red.dit+bot", database="bainsa"
        )
        tc = tconn.cursor(prepared=True)
        try:

            postsData = [p for p in reddit.info(fullnames=["t3_" + p for p in posts])]
            for submission in postsData:
                # Update the post data
                # Do some processing on the data to convert praw objects to strings
                # Also convert booleans to integers
                process_post(tc, submission)
            missing = set(posts) - set([p.id for p in postsData])
            tc.executemany("UPDATE posts SET processed = 0 WHERE id = %s", [(m,) for m in missing])
            print(f"Processed {len(postsData)} posts")
            tconn.commit()
            # Commit the changes to the database
            # conn.commit()
        except Exception as e:
            tqdm.tqdm.write(f"Error with post {posts}: {e}")

            # Rollback the changes
            tconn.rollback()

            # Fallback to processing posts one by one
            for post in posts:
                submission = reddit.submission(id=post)
                try:
                    process_post(tc, submission)
                except prawcore.exceptions.ResponseException:
                    tqdm.tqdm.write(
                        f"Error with post {post} (Post / Comment might be deleted or banned)"
                    )
                    tc.execute("UPDATE posts SET processed = 0 WHERE id = ?", (post,))
                except Exception as e:
                    tqdm.tqdm.write(f"Error with post {post}: {e}")
            tconn.commit()

        tconn.close()
        # Close the connection

    # Split the list into chunks of 100
    postList = [postList[i : i + 100] for i in range(0, len(postList), 100)]

    thread_map(process_posts, postList, max_workers=8, chunksize=8, position=1)


conn.close()
