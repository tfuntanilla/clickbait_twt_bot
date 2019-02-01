#### Fake Buzz Twitter Bot
Tweets fake clickbait headlines every hour. Key words are identified from the headline and are use to search for an 
image to be posted along with the tweet message.

Uses [markovify](https://github.com/jsvine/markovify) markov chains to generate the headlines and 
[Google Custom Search API](https://developers.google.com/api-client-library/python/apis/customsearch/v1#sample) to 
search for public domain images. [NLTK](https://www.nltk.org/) is used for identifying key words.

Clickbait data: https://github.com/bhargaviparanjape/clickbait/tree/master/dataset
