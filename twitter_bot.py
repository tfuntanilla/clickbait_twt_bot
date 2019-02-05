import datetime
import os
import string
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
    print(str(datetime.datetime.now()) + " Searching image for '" + query + "'...")
    res = api.cse().list(cx=cse_id, q=query, fileType='gif png jpg', num=10, safe='active', searchType='image')\
        .execute()

    if 'items' in res:
        for i, img in enumerate(res['items']):
            try:
                image_url = res['items'][i]['link']
                print(str(datetime.datetime.now()) + " Image: " + image_url)
                return image_url  # return first link that's found
            except KeyError:
                print("Image " + str(i) + " has no image link in search response.")
        print("No image found")
        return ""


#  Post basic tweet (without image)
def tweet_basic(api, tweet_msg):
    api.PostUpdate(tweet_msg)
    print(str(datetime.datetime.now()) + " Tweet success")


# Post tweet with image
def tweet_fake_buzz(api, tweet_msg, image_link):
    if not image_link:
        tweet_basic(api, tweet_msg)
    else:
        extension = image_link[image_link.rindex('.'):len(image_link)]  # get the extension of this image file
        filename = 'temp' + extension
        try:
            request = requests.get(image_link, stream=True)  # save the file temporarily
            if request.status_code == 200:
                with open(filename, 'wb') as image_link:
                    for chunk in request:
                        image_link.write(chunk)
                api.PostUpdate(status=tweet_msg, media=filename)  # tweet with image
                os.remove(filename)  # delete image file after tweeting
            else:
                print("Failed to download image: " + image_link)
                tweet_basic(api, tweet_msg)
        except IOError:
            print("Failed to download image: " + image_link)
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

    while True:
        tweet = create_headline(model, randint(40, 100))

        image_link = search_image(google_api, cse_id, tweet)  # search for image

        # identify key words in tweet to use for hashtags using part of speech tags
        # key words include nouns
        tokens = nltk.word_tokenize(str(tweet))
        tags = nltk.pos_tag(tokens)
        keywords_list = [word for word, pos in tags if (pos.startswith('N'))]

        # add question mark punctuation for interrogative headlines
        interrogative = ['Does', 'Do', 'Can', 'Should', 'Would', 'Could', 'How', 'Which']
        if tokens[0] in interrogative:
            tweet += "?"

        # add key words as hash tags, removing any punctuations in the hashtags
        if keywords_list:
            hashtag = ''.join(keywords_list).translate(str.maketrans('', '', string.punctuation))
            tweet += " #" + hashtag
        print(str(datetime.datetime.now()) + " Tweet: " + tweet)

        # post to twitter
        tweet_fake_buzz(twitter_api, tweet, image_link)

        print(str(datetime.datetime.now()) + " Success.")

        sleep(3600)  # tweet every hour


if __name__ == "__main__":
    main()
