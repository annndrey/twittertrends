#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import of the twitter lib to send requests to Twitter API
import tweepy
# requests lib is to query Wikipedia REST API
import requests
# re is the Regular Expressions lib
import re

# here are the required settings for twitter api, you can obtain your own keys here:
# https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html
# https://www.slickremix.com/docs/how-to-get-api-keys-and-tokens-for-twitter/
consumer_key = 'qtKbnBHNX3a3cpimtOM5CJr30'
consumer_secret = '5w2GrdQwxhvk2QZM7Ff2D9iJPVB0jylfnCyopgT3kX4zRhCd7t'
access_token = '2757010550-ra3TbUvMUcTZY2WoUqWQxVjg1EFMZlf8whryWOk'
access_token_secret = 'b9ngBX2gPELSZcvSFSKWcfJShejNZk8tk0kattbu9Vp7Y'

# Uppercase regex, it finds all words that starts from capital and the next letter is non-capital
uppercase = re.compile('[A-Z][^A-Z]*')

# here we create a single route for the Flask app, the root path. 
# now the app will be accesible at http://[your ip or localhost]/

def twitter_trends_to_wiki():
    # here we authenticate on twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # and here we got access to twitter api
    api = tweepy.API(auth)

    # Yahoo! Where On Earth ID 1 = worldwide
    # 23424977 USA
    # Here we query the twittet api for trending tweets for USA, for example. 
    # You can always get an YWOID for a particular place here:
    # http://woeid.rosselliot.co.nz/
    # 1 is for worldwide
    trends = api.trends_place(23424977)

    # here we save trends data to a local variable 
    data = trends[0]
    trends = data['trends']
    
    # now we iterate over all trending hashtags 
    for trnd in trends:
        # we extract the hashtag from trending data
        hashtag = trnd['name']

        # and perform some checks.
        if " " in hashtag:
            # space separated tags
            cleaned_tag = hashtag
        else:
            # find all uppercase tags and split it into space separated words
            uppercase_words = uppercase.findall(hashtag)
            if len(uppercase_words) > 0:
                # Check for abbreviated words, if length of all elements of a list is 1, i.e. 
                # we got something like ['A', 'A', 'B'] then it was abbreviated
                allequal = all([len(wd)==1 for wd in uppercase_words])
                if allequal:
                    cleaned_tag = "".join(uppercase_words)
                else:
                    cleaned_tag = " ".join(uppercase_words)
            else:
                # the rest are single words, we just remove the # symbol from tag
                cleaned_tag = hashtag.replace('#', '')
                
        # as long as we got cleaned tags we can perform wiki search
        wiki = requests.get("https://en.wikipedia.org/api/rest_v1/page/summary/%s" % cleaned_tag)
        # if something found, we parse the result and save it to the dict
        if wiki.status_code == 200:
            wiki_res = wiki.json()
            wiki_summary = wiki_res['extract']
            wiki_url = wiki_res['content_urls']['desktop']['page']
            wiki_title = wiki_res['title']
        # if there is nothing found, we save Nothing found messages
        else:
            wiki_summary = "Nothing found on %s" % cleaned_tag
            wiki_url = ""
            wiki_title = "Nothing found"

        print("-"*80)
        # on python string formatting you can read here:
        # https://docs.python.org/2/tutorial/inputoutput.html
        # we put named placeholders in the string and pass named arguments to format function
        print(u"{tag} : {name}".format(tag=hashtag, name=wiki_title))
        print(u"{indent}Summary: {summary}".format(indent=" "*(len(hashtag)+3), summary=wiki_summary))
        print(u"{indent}URL: {url}".format(indent=" "*(len(hashtag)+3), url=wiki_url))
    
# we check if the script is started from the commandline
if __name__ == '__main__':
    twitter_trends_to_wiki()
