# BAINSACryptocurrencies

## Data Gathering

### Reddit

- #### `reddit/search.py`:

  - This script is used to gather data from Reddit. It uses the Pushshift API to gather data using search queries. It gathers post IDs of the posts that match the search query and saves them into a SQLite database.

- #### `reddit/fetch.py`:

  - This script is used to gather the contents of the posts and the comments from the post IDs that were gathered by the search.py script. It uses the official Reddit API to get the most recent data. Then it saves the data into the SQLite database.

  - Before running the script, it is necessary to create a Reddit app and get a client ID and client secret. You can find more information about creating a Reddit app [here](https://www.reddit.com/wiki/api).

  - The client ID and client secret should be added to a new file `secrets.json`

    JSON
    {
      "client_id": "YOUR_CLIENT_ID_HERE",
      "client_secrets": "YOUR_CLIENT_SECRET_HERE"
    }
    

### Twitter

- #### `twitter/twitter_scraper_selenium_fork`:
  - This is a fork of an already existing repository used to scrape from Twitter. Some modifications have been applied such as some optimization (in particular regarding reusing existing webdriver instances) to the performance that allowed us to collect enough tweets.
- #### `twitter/main.py`:
  - This script handles the logic behind the tweets to collect and how to do it. It is customizable and relies on the above-mentioned library.
- #### `twitter\EDA.ipynb`:
  - This notebook contains a few analyses that we ran on the Twitter DB that show how unreliable it can be/

### News
  - News has been collected from alphavantage using external apis and can be found on Google Drive.

### Data

The data we have collected so far is fairly complete, in particular for Reddit and alphavantage. Twitter has some problems in its query which makes it such that the tweets are most likely not independent of each other and in particular they tend to concentrate all towards midnight.
We plan to start by using only Reddit, news and cryptocurrency prices.


## Literature review
- Literature highlights important specifics of the Bitcoin market, including its susceptibility to large price fluctuations. Unlike stock markets, the Bitcoin market does not close, which makes it more welcoming to noise traders.
- Using the news is a good choice for inferring the sentiment because news is professionally and precisely written, reaches a broad audience, focuses on short-term sentiment, and provides a market-level view at a certain date. However, the news does not always capture the information of insiders like corporate documents do and focuses on events in the past. The internet-expressed sentiment because the internet is unregulated, all sorts of traders can openly display their views and opinions, and it is therefore not likely to contain any new information.
- Literature also describes the so-called "herd behaviour," where noise traders imitate the lucky noise traders who earned high returns. Past research shows that herd behaviour increases market volatility.
- One possible method for sentiment analysis is the dictionary-based approach, where words and their occurrences in the text are analyzed. However, this approach does not work well if the text contains sarcasm, jokes, or any other indirect text. Nevertheless, via regression and VAR-Granger analysis, no evidence was found that the sentiment of the news from leading international news providers affects Bitcoin returns, either positively or negatively.
- There are machine-learning approaches that use neural networks. However, they require the data to be labelled.

## Results and future approaches
The first tests we have run were autoregressive models on the returns. We have tried different combinations of log transformations and amount of lag, but we found no evidence that suggests that this is a viable way.
The next steps that we want to try are more complex regressive models including new covariates such as the volume of social media posts in a determined period of time and similar.  
The `regression` folder contains some utilities to transform and explore the data and it is the starting block for our future models