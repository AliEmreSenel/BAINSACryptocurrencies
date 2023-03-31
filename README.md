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
