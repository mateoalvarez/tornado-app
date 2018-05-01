import tweepy
import json
import os
from kafka import KafkaProducer
import logging

LOGGER = logging.getLogger(__name__)
class ExploiterTwitterStreamListener(tweepy.StreamListener):

    def __init__(self):
        super(ExploiterTwitterStreamListener, self).__init__()
        bootstrap_server = os.environ.get("KAFKA_BOOTSTRAP_SERVER", "kafka-server")
        kafka_topic = os.environ.get("KAFKA_TOPIC", "default-token")
        if bootstrap_server is None:
            LOGGER.error("There is no KAFKA_BOOTSTRAP_SERVER present in environment")
            return None
        if kafka_topic is None:
            LOGGER.error("There is no KAFKA_TOPIC present in environment")
            kafka_topic = "empty_topic"
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_server,
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.kafka_topic = kafka_topic

    def on_data(self, data):
        print(" -> I am going to write...")
        self.producer.send(self.kafka_topic, data)
        self.producer.flush()
        return True

    def on_status(self, status):
        print(status.text)

def generate_auth_object():
    collector_api_token = os.environ.get("TWITTER_CONSUMER_API_KEY", "qUBED8JONS1rdOXMGXxJw3KDK")
    collector_api_secret = os.environ.get("TWITTER_CONSUMER_API_SECRET","DUI0ICvIXTYE4SPxdBSRVlq3xEw1UDpcy6mZG2qWE1yyX3nH2M")
    collector_access_token = os.environ.get("TWITTER_CONSUMER_TOKEN", "245605482-rajqw4klordPOid8izXvAHBc8DhU8QliOFraCFqM")
    collector_access_secret = os.environ.get("TWITTER_CONSUMER_SECRET", "kYalUO9SmnLvcjXPIrRE0dSEDd2LhQBSBMPD57UgLvzse")
    auth = tweepy.OAuthHandler(collector_api_token, collector_api_secret)
    auth.set_access_token(collector_access_token, collector_access_secret)
    return auth

def runApplication():
    auth = generate_auth_object()
    myStreamListener = ExploiterTwitterStreamListener()
    words_to_track = os.environ.get("WORDS_TO_TRACK", "#bigdata, #machinelearning").split(',')
    myStream = tweepy.Stream(auth=auth, listener=myStreamListener)
    # Goal is to keep this process always going
    while True:
        try:
            myStream.filter(track=words_to_track)
        except:
            pass

if __name__ == '__main__':
    runApplication()
