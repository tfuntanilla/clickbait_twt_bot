import configparser
import os
from random import randint

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
def twitter_setup(config):
    api = twitter.Api(consumer_key=config['TWITTER']['API_KEY'],
                      consumer_secret=config['TWITTER']['API_SECRET_KEY'],
                      access_token_key=config['TWITTER']['ACCESS_TOKEN'],
                      access_token_secret=config['TWITTER']['ACCESS_TOKEN_SECRET'])
    return api


# Set up google api
def google_setup(config):
    api = build('customsearch', 'v1', developerKey=config['GOOGLE']['API_KEY'])
    return api


# Create a fake buzz headline using markov chain model
def create_headline(text_model, max_chars=60):
    return text_model.make_short_sentence(max_chars)


# Google search image based on query
def search_image(api, cse_id, query):
    res = api.cse().list(cx=cse_id, q=query, fileType='gif png jpg', imgSize='medium', num=5, rights='cc_publicdomain',
                         safe='active', searchType='image').execute()
    image_url = res['items'][0]['link']
    return image_url


# Posts tweet with image
def tweet_fake_buzz(api, tweet_msg, image_link):
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
        api.PostUpdate(tweet_msg)


def main():
    # nltk config, run once
    if './nltk_data' not in nltk.data.path:
        nltk.data.path.append('./nltk_data')

    # load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    cse_id = config['GOOGLE']['CSE_ID']  # for google image search

    # set up apis
    twitter_api = twitter_setup(config)
    google_api = google_setup(config)

    # create markov chain model
    model = markov_chain_setup("clickbait_data")

    tweet = create_headline(model, randint(30, 140))

    # identify key words in tweet to use for searching accompanying image using part of speech tags
    # key words include singular nouns, plural nouns, and proper nouns
    tokens = nltk.word_tokenize(str(tweet))
    tags = nltk.pos_tag(tokens)
    nouns_list = [word for word, pos in tags if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
    key_words = ' '.join(nouns_list)

    image_link = search_image(google_api, cse_id, key_words)  # search for image

    tweet_fake_buzz(twitter_api, tweet, image_link)  # tweet

    # while True:
    #     TODO hourly tweets
    #     sleep(3600)  # tweet every hour


if __name__ == "__main__":
    main()
