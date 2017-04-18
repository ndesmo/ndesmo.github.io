#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import sys

from ConfigParser import ConfigParser

config = ConfigParser()
config.readfp(open('config.ini', 'r'))

#Variables that contains the user credentials to access Twitter API 
access_token = config.get('setup', 'access_token')
access_token_secret = config.get('setup', 'access_token_secret')
consumer_key = config.get('setup', 'consumer_key')
consumer_secret = config.get('setup', 'consumer_secret')


#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status


if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    
    keywords = sys.argv[1:]
    print keywords

    #This line filter Twitter Streams to capture data by the keywords
    stream.filter(track=keywords)
