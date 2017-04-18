# http://adilmoujahid.com/posts/2014/07/twitter-analytics/

import json

from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews


tweets_data_path = 'brexit.txt'
output_file_path = 'brexit_sentiment.txt'

def extract_words(text):
    
    text = text.lower()
    text = re.sub(r'[^\w#\s]', ' ', text)
    
    return text.split()
    
def word_feats(words):
    return dict([(word, True) for word in words])
    
negids = movie_reviews.fileids('neg')
posids = movie_reviews.fileids('pos')
 
negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]
 
trainfeats = negfeats + posfeats

classifier = NaiveBayesClassifier.train(trainfeats)

with open(tweets_data_path, "r") as tweets_file:
    with open(output_file_path, 'w') as output_file:
        for line in tweets_file:
            try:
                
                tweet = json.loads(line)
                tweet_text = tweet['text']
    
                words = extract_words(tweet['text'])
                
                sentiment = classifier.classify(word_feats(words))
                data = { 
                    'tweet': tweet,
                    'sentiment': sentiment
                    }
            
                json.dump(data, output_file)
                output_file.write('\n')
                
            except:
                continue

