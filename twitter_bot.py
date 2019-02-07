import configparser
import datetime
import os
import string
import sys
from random import randint
from time import sleep

import markovify
import nltk
import requests
import twitter
from googleapiclient.discovery import build


def exit_on_error():
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


# Set up markov chain model
def markov_chain_setup(file_path):
    try:
        # read the corpus as string
        with open(file_path) as f:
            text = f.read()
            text = text.replace("\n\n", "\n")  # remove extra newline

        # build the model
        text_model = markovify.NewlineText(text, state_size=4)
        return text_model
    except IOError:
        print("Failed to read corpus file: " + file_path)
        exit_on_error()


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
                print("Image " + str(i) + " has no image link in search response")

        print("No image found")
        return ""


#  Post basic tweet (without image)
def tweet_basic(api, tweet_msg):
    api.PostUpdate(tweet_msg)
    print(str(datetime.datetime.now()) + " Tweet success")


# Post tweet with image
def tweet_fake_buzz(api, tweet_msg, image_file):
    try:
        if not image_file:
            tweet_basic(api, tweet_msg)
        else:
            api.PostUpdate(status=tweet_msg, media=image_file)  # tweet with image
            os.remove(image_file)  # delete image file after tweeting
    except twitter.TwitterError:
        print(str(datetime.datetime.now()) + " Twitter API error")


def main():
    if len(sys.argv) != 2:
        print("Path to config.ini must be passed as argument.")
        exit_on_error()

    # read config file
    config = configparser.ConfigParser()
    try:
        config.read(sys.argv[1])
    except IOError:
        print("Failed to read config file: " + sys.argv[1])
        exit_on_error()

    # set up apis
    twitter_api = twitter_setup(config)
    google_api = google_setup(config)
    cse_id = config.get('GOOGLE', 'CSE_ID')

    # create markov chain model
    model_clickbait = markov_chain_setup("clickbait_data_filtered.txt")
    model_non_clickbait = markov_chain_setup("non_clickbait_data_filtered.txt")
    model = markovify.combine([model_clickbait, model_non_clickbait], [1.60, 1])

    # set nltk path
    if './nltk_data' not in nltk.data.path:
        nltk.data.path.append('./nltk_data')

    while True:
        # create headline
        tweet = create_headline(model, randint(40, 180))
        if tweet is None:
            print(str(datetime.datetime.now()) + " Markov chain model failed to generate a tweet.")
        else:
            print(str(datetime.datetime.now()) + " Headline: " + tweet)

            # tokenized headline
            tokens = nltk.word_tokenize(str(tweet))

            # add question mark punctuation for interrogative headlines
            interrogative = ['Does', 'Do', 'Can', 'Should', 'Would', 'Could', 'How', 'Which', "Is", "Are", "Was"]
            if tokens[0] in interrogative:
                tweet += "?"

            # identify key words in tweet to use for hashtags using parts-of-speech tags
            # nouns only, tagger isn't accurate so remove helping verbs
            verbs = ["am", "are", "is", "was", "were", "be", "being", "been", "have", "has", "had", "shall", "will",
                     "do", "does", "did", "may", "must", "might", "can", "could", "would", "should", "who", "what",
                     "why", "your", "you", "their", "or"]
            tags = nltk.pos_tag(tokens)
            keywords_list = [word for word, pos in tags if (pos.startswith('N') and word.lower() not in verbs)]
            query_words = [word for word, pos in tags if (pos.startswith('N') or pos.startswith('J'))]

            print(str(datetime.datetime.now()) + " Identified key words: " + str(keywords_list))
            print(str(datetime.datetime.now()) + " Identified query words: " + str(query_words))

            # add key words as hash tags, removing any punctuations in the hashtags
            for kw in keywords_list:
                tweet += " #" + kw.translate(str.maketrans('', '', string.punctuation))

            # full tweet
            print(str(datetime.datetime.now()) + " Tweet: " + tweet)

            # search for image to post with tweet message
            image = search_image(google_api, cse_id, ' '.join(query_words))

            # post to twitter
            tweet_fake_buzz(twitter_api, tweet, image)

            print(str(datetime.datetime.now()) + " Done.")

            sleep(300)  # tweet every 5 minutes


if __name__ == "__main__":
    main()
