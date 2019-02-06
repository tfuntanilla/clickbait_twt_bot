import datetime
import os
import string
import sys
from random import randint
from time import sleep

import configparser
import markovify
import nltk
import requests
import twitter
from googleapiclient.discovery import build


# Set up markov chain model
def markov_chain_setup(file_path):
    try:
        # read the corpus as string
        with open(file_path) as f:
            text = f.read()
            text = text.replace("\n\n", "\n")  # remove extra newline

        # build the model
        text_model = markovify.NewlineText(text)
        return text_model
    except IOError:
        print("Failed to read " + file_path)
        print("Exiting program.")
        exit(1)


# Set up twitter api
def twitter_setup(config):
    api = twitter.Api(consumer_key=config.get('TWITTER', 'API_KEY'),
                      consumer_secret=config.get('TWITTER', 'API_SECRET_KEY'),
                      access_token_key=config.get('TWITTER', 'ACCESS_TOKEN'),
                      access_token_secret=config.get('TWITTER', 'ACCESS_TOKEN_SECRET'))
    return api


# Set up google api
def google_setup(config):
    api = build('customsearch', 'v1', developerKey=config.get('GOOGLE', 'API_KEY'))
    return api

# Create a fake buzz headline using markov chain model
def create_headline(text_model, max_chars=60):
    return text_model.make_short_sentence(max_chars)


# Google search image based on query
def search_image(api, cse_id, query):
    print(str(datetime.datetime.now()) + " Searching image for '" + query + "'...")
    res = api.cse().list(cx=cse_id, q=query, fileType='gif png jpg', num=10, safe='active', searchType='image') \
        .execute()

    if 'items' in res:
        for i, img in enumerate(res['items']):
            try:
                image_url = res['items'][i]['link']
                print(str(datetime.datetime.now()) + " Image: " + image_url)

                try:
                    extension = image_url[image_url.rindex('.'):len(image_url)]  # get the extension of this image file
                    temp_image_file = 'temp' + extension

                    request = requests.get(image_url, stream=True)  # save the file temporarily
                    if request.status_code == 200:
                        with open(temp_image_file, 'wb') as image_url:
                            for chunk in request:
                                image_url.write(chunk)
                        return temp_image_file
                    else:
                        print("Failed to download image: " + image_url)

                except IOError:
                    print("Failed to download image: " + image_url)

            except KeyError:
                print("Image " + str(i) + " has no image link in search response.")

        print("No image found")
        return ""


#  Post basic tweet (without image)
def tweet_basic(api, tweet_msg):
    api.PostUpdate(tweet_msg)
    print(str(datetime.datetime.now()) + " Tweet success")


# Post tweet with image
def tweet_fake_buzz(api, tweet_msg, image_file):
    if not image_file:
        tweet_basic(api, tweet_msg)
    else:
        api.PostUpdate(status=tweet_msg, media=image_file)  # tweet with image
        os.remove(image_file)  # delete image file after tweeting


def main():

    if len(sys.argv) != 3:
        print("Path to config.ini must be passed as 1st arg and path to the clickbait corpus must be passed as the "
              "2nd arg")
        print("Exiting program.")
        exit(1)

    # read config file
    config = configparser.ConfigParser()
    try:
        config.read(sys.argv[1])
    except IOError:
        print("Invalid config.ini")
        print("Exiting")
        exit(1)

    # set up apis
    twitter_api = twitter_setup(config)
    google_api = google_setup(config)
    cse_id = config.get('GOOGLE', 'CSE_ID')

    # set nltk path
    if './nltk_data' not in nltk.data.path:
        nltk.data.path.append('./nltk_data')

    # create markov chain model
    model = markov_chain_setup(sys.argv[2])

    while True:
        # create headline
        tweet = create_headline(model, randint(40, 100))
        print(str(datetime.datetime.now()) + " Headline: " + tweet)

        # add question mark punctuation for interrogative headlines
        tokens = nltk.word_tokenize(str(tweet))
        interrogative = ['Does', 'Do', 'Can', 'Should', 'Would', 'Could', 'How', 'Which']
        if tokens[0] in interrogative:
            tweet += "?"

        # identify key words in tweet to use for hashtags using part of speech tags
        # key words include nouns, tagger isn't accurate so remove verbs
        verbs = ["am", "are", "is", "was", "were", "be", "being", "been", "have", "has", "had", "shall", "will",
                 "do", "does", "did", "may", "must", "might", "can", "could", "would", "should"]
        tags = nltk.pos_tag(tokens)
        keywords_list = [word for word, pos in tags if (pos.startswith('N') and word.lower() not in verbs)]
        print(str(datetime.datetime.now()) + " Identified key words: " + str(keywords_list))

        # add key words as hash tags, removing any punctuations in the hashtags
        if 0 <= len(keywords_list) <= 3:
            hashtag = (''.join(keywords_list)).translate(str.maketrans('', '', string.punctuation))
            tweet += " #" + hashtag
        else:
            ht_set_one = (keywords_list[0] + keywords_list[1]).translate(str.maketrans('', '', string.punctuation))
            ht_set_two = (keywords_list[-2] + keywords_list[-1]).translate(str.maketrans('', '', string.punctuation))
            tweet += " #" + ht_set_one + " #" + ht_set_two

        # full tweet
        print(str(datetime.datetime.now()) + " Tweet: " + tweet)

        # search for image to post with tweet
        image = search_image(google_api, cse_id, ' '.join(keywords_list))

        # post to twitter
        tweet_fake_buzz(twitter_api, tweet, image)

        print(str(datetime.datetime.now()) + " Success.")

        sleep(3600)  # tweet every hour


if __name__ == "__main__":
    main()
