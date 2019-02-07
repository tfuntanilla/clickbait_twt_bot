#### Fake Buzz Twitter Bot
Tweets fake clickbait headlines every 5 minutes. Key words are identified in the generated tweet and are used to search 
for an image to be posted along with the tweet.

Uses [markovify](https://github.com/jsvine/markovify) markov chains to generate the headlines and 
[Google Custom Search API](https://developers.google.com/api-client-library/python/apis/customsearch/v1#sample) to 
search for images. [NLTK](https://www.nltk.org/) is used for identifying key words for hashtags.

Download full corpus of clickbait and non-clickbait headlines from: 
https://github.com/bhargaviparanjape/clickbait/tree/master/dataset

The path to config.ini file is a required command-line argument.
See ```example_config.ini``` for config.ini file format.

How to run from command line:
```
python setup.py install
python twitter_bot.py path_to_config.ini
```


