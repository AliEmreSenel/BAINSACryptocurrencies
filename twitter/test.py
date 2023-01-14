from twitter_scraper_selenium_fork import scrape_keyword, scrape_keyword_with_api
from datetime import datetime, timedelta
from os.path import isfile


def save_tweets(since: datetime, until: datetime, per_day: int, hashtags: list, filename: str, query_parameters,
                delta=timedelta(days=1)):
    for keyword in hashtags:
        print(f"Starting with {keyword}")
        while since < until:
            # print(f"Downloading: {since.date()}")
            # print(f"Time: {datetime.now()}")
            name = filename + f"-{keyword}-{since.date()}-{per_day}"
            # print(name)
            if isfile(name + ".json"):
                print(f"{name} already existing")
                since = since + delta
                continue
            scrape_keyword(keyword=keyword, filename=name, since=str(since.date()),
                           until=str((since + delta).date()), tweets_count=per_day,
                           query_parameters=query_parameters, driver_to_close=False)

            since = since + delta

    # safety feature
    from twitter_scraper_selenium_fork.keyword import Keyword
    Keyword.close_static_driver()


if __name__ == '__main__':
    query_parameters = {
        "min_faves": 100,
    }

    save_tweets(datetime(2022, 10, 1), datetime(2022, 10, 31), 20, ["crypto"], "scraped-tweets",
                query_parameters)
