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


KEYWORDS = ["crypto", "dodgecoin", "btc", "ethereum", "bitcoin", "ripple", "solana"]

if __name__ == '__main__':
    import sys

    args = sys.argv

    d_s = int(args[-6])
    m_s = int(args[-5])
    y_s = int(args[-4])
    d_e = int(args[-3])
    m_e = int(args[-2])
    y_e = int(args[-1])

    start = datetime(y_s, m_s, d_s)
    end = datetime(y_e, m_e, d_e)


    print(f"Starting program from {start.date()} to {end.date()}")

    query_parameters = {
        "min_faves": 10,
    }

    save_tweets(start, end, 20000, KEYWORDS, "scraped-tweets",
                query_parameters)

# todo: oracle vps


# instructions:
# the function save tweets does the hard work, the algorithm is parallelized on the time frame, which means that
# one should run different instances with different time windows. With little work we can change it to keywords, but it
# is useless in my opinion as they are fixed.
# The syntax is as follows: python3 main.py DAY_START MONTH_START YEAR_START DAY_END MONTH_END YEAR_END
# Note that the range is (inclusive, exclusive)
# The code is slightly verbose but most of the output is due to the webdriver, you can comment out parts
# d="2021-01-01"; until [[ $d > $(date +"%Y-%m-%d") ]]; do echo $(date -d "$d" +"%d %m %Y") $(date -d "$d + 1 days" +"%d %m %Y"); d=$(date -I -d "$d + 1 day"); done |parallel python main.py
