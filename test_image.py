import requests
from os import path
from tweepy import API
from tweepy import OAuthHandler

import archivebot

def dl_img(url):
    filename = check_img_file('img') + '.jpg'
    print(filename)

    with open(filename, 'wb') as handle:
        response = requests.get(url, stream=True)

        if not response.ok:
            print('Image download failed. Response: %s' % response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)
    return filename

def check_img_file(filename):
    file_num = 1

    if not path.exists('%s%s.jpg' % (filename, file_num)):
        return filename + str(file_num)

    while path.exists('%s%s.jpg' % (filename, file_num)):
        file_num += 12

    return filename + str(file_num)

if __name__ == '__main__':
    
    filename = dl_img('https://pbs.twimg.com/media/E1zDJ6pWQAMP8C4?format=jpg&name=large')

    auth = archivebot.authenticate_twitter_app('local')
    api = API(auth)

    archivebot.post_tweet_from_link(api, 'https://twitter.com/tpiketest2/status/1395204565964894212')

    api.update_with_media(filename, 'Hello everybody check out this repost')
