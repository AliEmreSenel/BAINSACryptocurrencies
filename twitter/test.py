from twitter_scraper_selenium import scrape_keyword, scrape_keyword_with_api
from datetime import datetime, timedelta
from os.path import isfile

def save_tweets(since: datetime, until: datetime, per_day: int, hashtags: list, filename: str):
    for keyword in hashtags:
        print(f"Starting with {keyword}")
        while since < until:
            print(f"{since.date()}  -  {until.date()}")
            name = filename + f"-{keyword}-{since.date()}"
            if isfile(name):
                continue
            scrape_keyword(keyword=keyword, filename=name, since=str(since.date()),
                           until=str((since + timedelta(days=1)).date()), tweets_count=per_day)


if __name__ == '__main__':
    save_tweets(datetime(2020, 10, 1), datetime(2020, 10, 31), 10, ["crypto", "btc"], "scraped-tweets")
