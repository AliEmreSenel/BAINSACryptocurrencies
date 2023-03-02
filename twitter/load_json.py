import pandas as pd
import json

DIR = "data/"
# different amount of rows, does not work
# df = pd.read_json("data/scraped-tweets-crypto-2021-01-05-20.json")


from os import walk

files = []
for (dirpath, dirnames, filenames) in walk(DIR):
    files.extend(filenames)
    break

files.remove("geckodriver.log")


tweets = []
for name in files:
    # print(name)
    with open(DIR + name, "r") as f:
        d = json.loads(f.read())
    for x in d.items():
        # print(x, d)
        # input()
        x[1]["category"] = name.split("-")[2]
        tweets.append(x[1])


df = pd.DataFrame(tweets)

df.to_csv("tweeter_data_pandas.csv.csv")