import praw
import tqdm
import sqlite3
import json

# Connect to the database

conn = sqlite3.connect("reddit.db")
c = conn.cursor()

# Create the tables
# Note that we are using the IF NOT EXISTS clause to avoid errors if the tables already exist
# Note that we are using the PRIMARY KEY clause to avoid duplicate entries

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
        user_agent=secrets["user_agent"],
    )

    postList = []

    # Get posts that have not been processed
    c.execute("SELECT * FROM posts WHERE processed is NULL")

    print("Getting posts")

    for row in tqdm.tqdm(c.fetchall()):
        postList.append(row[0])

    for post in tqdm.tqdm(postList):
        #        tqdm.tqdm.write("Processing post: " + post)
        try:
            submission = reddit.submission(id=post)

            # Update the post data
            # Do some processing on the data to convert praw objects to strings
            # Also convert booleans to integers
            c.execute(
                "UPDATE posts SET title = ?, author = ?, created_utc = ?, subreddit = ?, score = ?, num_comments = ?, permalink = ?, url = ?, selftext = ?, over_18 = ?, is_video = ?, is_original_content = ?, is_self = ?, is_meta = ?, is_crosspostable = ?, is_reddit_media_domain = ?, is_robot_indexable = ?, is_gallery = ?, processed = true WHERE id = ?",
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
            c.execute(
                "UPDATE posts SET comments_processed = true WHERE id = ?", (post,)
            )

            # Commit the changes to the database
            conn.commit()
        except Exception as e:
            tqdm.tqdm.write(f"Error with post {post}: " + str(e))

# Close the connection
conn.close()
