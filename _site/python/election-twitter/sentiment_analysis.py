# http://adilmoujahid.com/posts/2014/07/twitter-analytics/

import json
import pandas as pd
import matplotlib.pyplot as plt

import random
from pandas.io.json import json_normalize

tweets_data_path = 'brexit_sentiment.txt'

tweets_data = []

i = 0
with open(tweets_data_path, "r") as tweets_file:
    for line in tweets_file:
        i += 1
        try:
            if i % 20 == 0:
                tweet = json.loads(line)
                tweets_data.append(tweet)
        except:
            continue
        
tweets = json_normalize(tweets_data)

tweets_by_sentiment = tweets['sentiment'].value_counts()

fig, ax = plt.subplots()
ax.tick_params(axis='x', labelsize=15)
ax.tick_params(axis='y', labelsize=10)
ax.set_xlabel('Sentiment', fontsize=15)
ax.set_ylabel('Number of tweets' , fontsize=15)
ax.set_title('Sentiment of tweets', fontsize=15, fontweight='bold')
tweets_by_sentiment.plot(ax=ax, kind='bar', color='red')




