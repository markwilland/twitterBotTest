from tweepy import API
from tweepy import OAuthHandler
import requests
import sys
from os import environ
from time import sleep
from datetime import datetime
import json

import twitterCredentials

#### TWITTER AUTH FUNCTION ####
def authenticate_twitter_app(context):
    if context == 'heroku':
        auth = OAuthHandler(environ['CONSUMER_KEY'], environ['CONSUMER_SECRET'])
        auth.set_access_token(environ['ACCESS_TOKEN'], environ['ACCESS_TOKEN_SECRET'])
        return auth

    else:
        auth = OAuthHandler(twitterCredentials.CONSUMER_KEY, twitterCredentials.CONSUMER_SECRET)
        auth.set_access_token(twitterCredentials.ACCESS_TOKEN, twitterCredentials.ACCESS_TOKEN_SECRET)
        return auth

# format JSON for debugging
def pretify_json(obj):
    return json.dumps(obj, indent=4, sort_keys=True)

def img_from(url):
    with open('tweet_image.jpg', 'wb') as handle:
        response = requests.get(url, stream=True)

        if not response.ok:
            print('Image download failed. Response: %s' % response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

# returns a timestamp of the last tweet
def get_last_tweet(api):
    tweets = api.user_timeline(count=1)

    if not tweets:
        print('no tweets posted')
        return ''

    else:
        print('Found latest tweet: ')
        print(pretify_json(tweets[0]._json))
        tweet_time = tweets[0]._json['created_at']
        tweet_date_time = datetime.strptime(tweet_time, '%a %B %d %X %z %Y')
        print('Date time object: %s' % str(tweet_date_time))
        
        tweet_timestamp = datetime.timestamp(tweet_date_time)
        print('Timestamp: %s' % tweet_timestamp)

        return tweet_timestamp

def post_tweet_from_link(api, tweet_url):
    tweet_id_with_param = tweet_url.rsplit('/', 1)[-1]
    print(tweet_id_with_param)
    tweet_id_str = tweet_id_with_param.split('?', 1)[0]
    print('Removing ? char: %s' % tweet_id_str)
    tweet_id = int(tweet_id_str)


    print('Got tweet id from url: %s' % tweet_id)

    tweet = api.statuses_lookup(id_=[tweet_id], tweet_mode='extended')
    print(pretify_json(tweet[0]._json))

    return (tweet[0]._json['full_text'], 'temp')

# def get_tweet(api, tweet_url):
#     tweet_id = int(tweet_url.rsplit('/', 1)[-1])
#     print('Got tweet id from url: %s' % tweet_id)

#     tweet = api.get_status(id=tweet_id, tweet_mode='extended')

#     print('text only: %s' + pretify_json(tweet._json))


def post_next_tweets(api, last_tweet_timestamp):
    latest_timestamp = last_tweet_timestamp
    next_posts = []
    dms = api.list_direct_messages(count=20)

    if not dms:
        print('no dms')
        return last_tweet_timestamp

    for dm in dms:
        print(pretify_json(dm._json))
        dm_timestamp = int(dm._json['created_timestamp'])
        timestamp_seconds = round(dm_timestamp / 1000)
        print('DM Timestamp: %s' % timestamp_seconds)

        if timestamp_seconds <= last_tweet_timestamp or not dm._json['message_create']['message_data']['entities']['urls']:
            print('No more tweets to post')
            break
        else:
            print('Posting new tweet from dm!')
            print('DM text: %s \nDM timestamp: %s' % (dm._json['message_create']['message_data']['text'], timestamp_seconds))
            next_posts.append({'url':dm._json['message_create']['message_data']['entities']['urls'][0]['expanded_url'], 'timestamp':timestamp_seconds})     
    
    print('list of new posts: %s' % list(reversed(next_posts)))

    # for post in reversed(next_posts):
    #     print('Making new post: %s' % post)
    #     api.update_status(post_tweet_from_link(api, post['url']))
    #     latest_timestamp = post['timestamp']
    print('done')
    return

if __name__ == '__main__':
    # main loop
    print('Authenticating...')

    # heroku = running from server, anything else = local
    auth = authenticate_twitter_app('local')
    api = API(auth)

    


    # print('Authentication successful!')

    # print('Looking for latest tweet on timeline...')
    # last_tweet_timestamp = get_last_tweet(api)
    
    # while True:
    #     print('Current latest tweet posted at: %s' % last_tweet_timestamp)
        
    #     last_tweet_timestamp = post_next_tweets(api, last_tweet_timestamp)
    #     print('Waiting 5 minutes....')
    #     sleep(300)