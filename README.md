#### Fake Buzz Twitter Bot
Tweets fake clickbait headlines every hour. The generated tweet is used to search for an image to be posted along 
with it.

Uses [markovify](https://github.com/jsvine/markovify) markov chains to generate the headlines and 
[Google Custom Search API](https://developers.google.com/api-client-library/python/apis/customsearch/v1#sample) to 
search for images. [NLTK](https://www.nltk.org/) is used for identifying key words for hashtags.

Dataset: https://github.com/bhargaviparanjape/clickbait/tree/master/dataset

The following parameters must be passed as environment variables:
```
TWITTER_API_KEY
TWITTER_API_SECRET_KEY
TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET
GOOGLE_API_KEY
GOOGLE_CSE_ID
```


