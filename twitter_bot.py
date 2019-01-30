import configparser
import os
from random import randint
from time import sleep

import requests
import twitter

from scrap import markovify


def markov_chain_setup(file_path):
    # read the corpus as string
    with open(file_path) as f:
        text = f.read()

    # build the model
    text_model = markovify.NewlineText(text)
    return text_model


def twitter_setup():
    config = configparser.ConfigParser()
    api = twitter.Api(consumer_key=config['CONSUMER_KEY'],
                      consumer_secret=config['CONSUMER_SECRET'],
                      access_token_key=config['ACCESS_TOKEN'],
                      access_token_secret=config['ACCESS_TOKEN_SECRET'])
    return api


def make_headline(text_model, max_chars=60):
    return text_model.make_short_sentence(max_chars)


# TODO
def search_for_image(key_words):
    # use google api to search and download an image
    print()
    url = ''
    # if there are no good images, use this
    # encoded_image_path = text_to_image.encode("Hello World!", "temp.png")
    return url


def tweet(api, url, message):
    extension = url[url.rindex('.'):-1]
    filename = 'temp' + extension
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)
        api.update_with_media(filename, status=message)
        os.remove(filename)
    else:
        print("Unable to download image")


def main():

    model = markov_chain_setup("clickbait_data")
    api = twitter_setup()

    while True:
        message = make_headline(model, randint(30, 140))
        # TODO get key words from message
        key_words = []
        url = search_for_image(key_words)
        tweet(api, url, message)
        sleep(3600)  # tweet every hour


if __name__ == "__main__":
    main()
