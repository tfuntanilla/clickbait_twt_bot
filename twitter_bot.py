import datetime
import os
from random import randint
from time import sleep

import markovify
import nltk
import requests
import twitter
from googleapiclient.discovery import build


# Set up markov chain model
def markov_chain_setup(file_path):
    # read the corpus as string
    with open(file_path) as f:
        text = f.read()

    # build the model
    text_model = markovify.NewlineText(text)
    return text_model


# Set up twitter api
def twitter_setup():
    api = twitter.Api(consumer_key=os.environ['TWITTER_API_KEY'],
                      consumer_secret=os.environ['TWITTER_API_SECRET_KEY'],
                      access_token_key=os.environ['TWITTER_ACCESS_TOKEN'],
                      access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
    return api


# Set up google api
def google_setup():
    api = build('customsearch', 'v1', developerKey=os.environ['GOOGLE_API_KEY'])
    return api


# Create a fake buzz headline using markov chain model
def create_headline(text_model, max_chars=60):
    return text_model.make_short_sentence(max_chars)


# Google search image based on query
def search_image(api, cse_id, query):
    print(str(datetime.datetime.now()) + " Searching image...")
    try:
        res = api.cse().list(cx=cse_id, q=query, fileType='gif png jpg', imgSize='medium', num=5,
                             rights='cc_publicdomain', safe='active', searchType='image').execute()
        image_url = res['items'][0]['link']
        print(str(datetime.datetime.now()) + " Image: " + image_url)
        return image_url
    except KeyError:
        return ""


def tweet_basic(api, tweet_msg):
    api.PostUpdate(tweet_msg)
    print(str(datetime.datetime.now()) + " Tweet success")


# Posts tweet with image
def tweet_fake_buzz(api, tweet_msg, image_link):
    if image_link == "":
        tweet_basic(api, tweet_msg)
    else:
        extension = image_link[image_link.rindex('.'):len(image_link)]  # get the extension of this image
        filename = 'temp' + extension
        try:
            request = requests.get(image_link, stream=True)  # save the file temporarily
            if request.status_code == 200:
                with open(filename, 'wb') as image_link:
                    for chunk in request:
                        image_link.write(chunk)
                api.PostUpdate(status=tweet_msg, media=filename)  # tweet with image
                os.remove(filename)
            else:
                print("Unable to download image")
                api.PostUpdate(tweet_msg)  # simple tweet
        except IOError:
            tweet_basic(api, tweet_msg)


def main():
    # set nltk path
    if './nltk_data' not in nltk.data.path:
        nltk.data.path.append('./nltk_data')

    # set up apis
    twitter_api = twitter_setup()
    google_api = google_setup()
    cse_id = os.environ['GOOGLE_CSE_ID']

    # create markov chain model
    model = markov_chain_setup("clickbait_data")

    # tweet every hour
    while True:
        tweet = create_headline(model, randint(30, 100))

        # identify key words in tweet to use for searching accompanying image using part of speech tags
        # key words include singular nouns and plural nouns
        tokens = nltk.word_tokenize(str(tweet))
        tags = nltk.pos_tag(tokens)
        key_words_list = [word for word, pos in tags if (pos.startswith('N'))]

        # add key words as hash tags
        tweet += " #" + ''.join(key_words_list)
        print(str(datetime.datetime.now()) + " Tweet: " + tweet)

        image_link = search_image(google_api, cse_id, ' '.join(key_words_list))  # search for image

        tweet_fake_buzz(twitter_api, tweet, image_link)  # tweet

        print(str(datetime.datetime.now()) + " Done.")

        sleep(3600)


if __name__ == "__main__":
    main()
