# BAINSACryptocurrencies

## Data Gathering

### Reddit

- #### `reddit/search.py`:

  - This script is used to gather data from Reddit. It uses the Pushshift API to gather data using search queries. It gathers post IDs of the posts that match the search query and saves them into a SQLite database.

- #### `reddit/fetch.py`:

  - This script is used to gather the contents of the posts and the comments from the post IDs that were gathered by the search.py script. It uses the official Reddit API to get the most recent data. Then it saves the data into the SQLite database.

  - Before running the script, it is necessary to create a Reddit app and get a client ID and client secret. You can find more information about creating a Reddit app [here](https://www.reddit.com/wiki/api).

  - The client ID and client secret should be added to a new file `secrets.json`

    ```json
    {
      "client_id": "YOUR_CLIENT_ID_HERE",
      "client_secrets": "YOUR_CLIENT_SECRET_HERE"
    }
    ```

### Twitter

- #### `twitter/twitter_scraper_selenium_fork`:
  - This is a fork of an already existing repository used to scrape from twitter. Some modifications have been applied such as some optimization (in particular regarding reusing existing webdriver instances) to performance that allowed us to collect enough tweets.
- #### `twitter/main.py`:
  - This script actually handles the logic behind the tweets to collect and how to do it. It is customizable and relies on the above-mentioned library.
- #### `twitter\EDA.ipynb`:
  - This notebook contains a few analysis that we ran on the twitter DB that show how unreliable it can be/

### News
  - News have been collected from alphavantage using external apis and can be found on Google Drive.

### Data

The data we have collected so far is fairly complete, in particular for reddit and alphavantage. Twitter has some problems in its query which makes it such that the tweets are most likely not independent to each other and in particular they tend to concentrate all towards midnight.
Our plan is to start by using only reddit, news and cryptocurrencies prices.


## Literature review
- Literature highlights important specifics of the Bitcoin market, including its susceptibility to large price fluctuations. Unlike stock markets, the Bitcoin market does not close, which makes it more welcoming to noise traders.
- Using the news is a good choice for inferring the sentiment because news are professionally and precisely written, reaches a broad audience, focuses on short-term sentiment, and provides a market-level view at a certain date. However, the news do not always capture the information of insiders like corporate documents do, and focus on events in the past. The  internet-expressed sentiment because the internet is unregulated, all sorts of traders can openly display their views and opinions, and it is therefore not likely to contain any new information.
- Literature also describes the so-called "herd behavior," where noise traders imitate the lucky noise traders who earned high returns. Past research shows that herd behavior increases market volatility.
- One possible method for sentiment analysis is the dictionary-based approach, where words and their occurrences in the text are analyzed. However, this approach does not work well if the text contains sarcasm, jokes, or any other indirect text. Nevertheless, via regression and VAR-Granger analysis, no evidence was found that the sentiment of the news from leading international news providers has an effect on Bitcoin returns, either positive or negative.
- There are other machine learning approaches that use neural networks. However, this requires the data to be labeled.

## Results and future approaches
The first tests we have run were autoregressive models on the returns. We have tried different combinations of log transformations and amount of lag, but we found no evidence that suggests that this is a viable way.
The next steps that we want to try are more complex regressive models including new covariates such as volume of social media posts in a determined span of time and similar.  
The `regression` folder contains some utilities to transform and explore the data and it is the starting block for our future models