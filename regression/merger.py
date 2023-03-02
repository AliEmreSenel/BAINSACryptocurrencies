import pandas as pd

# btc_av = pd.read_csv("df_BTC_alphavantage_01_Feb.csv")
# eth_av = pd.read_csv("df_ETH_alphavantage_01_Feb.csv")
reddit_c = pd.read_csv("reddit_comments.csv")
reddit_p = pd.read_csv("reddit_posts.csv")
twitter = pd.read_csv("tweeter_data_pandas.csv")
twitter = twitter.drop(columns=["link"])

columns = ["id", "date", "content", "likes", "title", "author", "link", "other_scores", "replies",
           "topics", "social"]

# Reddit posts

reddit_p = reddit_p.rename(columns={
    "created_utc": "date",
    "num_comments": "replies",
    "subreddit": "topics",
    "url": "link",
    "selftext": "content",
    "score": "likes",
})

# not present columns: other_scores, social
reddit_p["other_scores"] = ""
reddit_p["social"] = "reddit"
reddit_p["date"] = pd.to_datetime(reddit_p["date"])


# merge inner to be used

# reddit_p["title"] = reddit_p["title"].astype("")
# reddit_p["author"] = reddit_p["author"].astype("string")
reddit_p["date"] = reddit_p["date"].astype("object")

z = list(twitter.columns)
z.sort()
twitter["name"] = twitter["name"] + " " + twitter["username"]
twitter = twitter.rename(columns={
    "tweet_id": "id",
    "name": "author",
    "posted_time": "date",
    "hashtags": "topics",
    "tweet_url": "link"
})

twitter["topics"] = twitter["topics"][:-1] + "," + twitter["category"] + "]"  # todo: be fixed
twitter = twitter.drop(["category"], axis=1)
twitter["social"] = "twitter"
twitter["title"] = ""
twitter["other_scores"] = ""
twitter["date"] = pd.to_datetime(twitter["date"])


# res = pd.merge(twitter, reddit_p, how="inner")
# res.head()
twitter["id"] = twitter["id"].astype("object")
twitter["replies"] = twitter["replies"].astype("float")
twitter["likes"] = twitter["likes"].astype("float")


# Reddit posts

reddit_c = reddit_c.rename(columns={
    "created_utc": "date",
    # "num_comments": "replies",
    "subreddit": "topics",
    "link_id": "link",
    "body": "content",
    "score": "likes",
})


reddit_c["date"] = pd.to_datetime(reddit_c["date"])

# not present columns: other_scores, social
reddit_c["other_scores"] = ""
reddit_c["replies"] = 0
reddit_c["social"] = "reddit"
reddit_c["title"] = ""
# merge inner to be used
res = pd.concat([twitter, reddit_p, reddit_c], ignore_index=True, join="inner")
res.to_csv("Aggregated_reddit_twitter.csv")
