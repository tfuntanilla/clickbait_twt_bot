import configparser
import os
from random import randint

import markovify
import requests
import twitter
from googleapiclient.discovery import build


def markov_chain_setup(file_path):
    # read the corpus as string
    with open(file_path) as f:
        text = f.read()

    # build the model
    text_model = markovify.NewlineText(text)
    return text_model


def twitter_setup(config):
    api = twitter.Api(consumer_key=config['TWITTER']['API_KEY'],
                      consumer_secret=config['TWITTER']['API_SECRET_KEY'],
                      access_token_key=config['TWITTER']['ACCESS_TOKEN'],
                      access_token_secret=config['TWITTER']['ACCESS_TOKEN_SECRET'])
    return api


def google_setup(config):
    api = build('customsearch', 'v1', developerKey=config['GOOGLE']['API_KEY'])
    return api


def make_headline(text_model, max_chars=60):
    return text_model.make_short_sentence(max_chars)


def search_for_image(api, cse_id, query):
    # use google api to search and download an image
    res = api.cse().list(cx=cse_id, q=query, imgSize='medium', num=5,
                         rights='cc_publicdomain', safe='medium', searchType='image').execute()
    image_url = res['items'][0]['link']
    return image_url


def tweet_basic(api, message):
    api.PostUpdate(message)


def tweet_fake_buzz(api, url, message):
    extension = url[url.rindex('.'):len(url)]
    filename = 'temp' + extension
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)
        api.PostUpdate(status=message, media=filename)
        os.remove(filename)
    else:
        print("Unable to download image")
        api.PostUpdate(message)


def main():
    
    # load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    cse_id = config['GOOGLE']['CSE_ID']  # for google image search

    # set up apis
    twitter_api = twitter_setup(config)
    google_api = google_setup(config)

    # create markov chain model
    model = markov_chain_setup("clickbait_data")

    message = make_headline(model, randint(30, 140))
    # TODO find most important words in message
    key_words = []
    url = search_for_image(google_api, cse_id, ' '.join(key_words))
    tweet_fake_buzz(twitter_api, url, message)

    # while True:
    #     TODO do stuff here
    #     sleep(3600)  # tweet every hour


if __name__ == "__main__":
    main()
