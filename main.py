# markov chain title and description generator from SHARE results

import random

import tweepy
import requests

import settings

OSF_URL = 'http://share-dev.osf.io/api/v1/app/6qajn/?q=source:plos&page:{}'


def get_title_and_description(pages=1):
    ''' Goes to the SHARE API endpoint and grab some pages
    of text from description, and returns a string
    '''
    title = ''
    description = ''
    for page in range(0, pages):
        items = requests.get(OSF_URL.format(page), verify=False)

        page_text = items.json()
        results = page_text['results']

        for item in results:
            description += item['description'] + ' '
            title += item['title'] + ' '

    return title, description


def make_markov_chain(text):
    ''' Takes input text as a string and returns a dict
    of markov chains'''

    markov_chain = {}
    words = text.split()

    for i in range(len(words) - 2):
        word_pair = (words[i], words[i + 1])
        if word_pair in markov_chain:
            markov_chain[word_pair] += [words[i + 2]]
        else:
            markov_chain[word_pair] = [words[i + 2]]

    return markov_chain


def get_character_count(line):
    count = 0
    for word in line:
        for char in word:
            count += 1
        # count += 1

    return count


def generate_line(markov_chain, title=False, title_words=10, twitter=False):
    ''' Takes a dict of markov chains and returns random text!'''

    start = ' '
    while not start[0][0].isupper():
        start = random.choice(markov_chain.keys())

    line = list(start)

    line_enders = ['?', '.', '!']

    if title:
        while len(line) < title_words:
            next_words = markov_chain[tuple(line[-2:])]
            line += [random.choice(next_words)]
    if twitter:
        while get_character_count(line) < 105:
            # print(get_character_count(line))
            next_words = markov_chain[tuple(line[-2:])]
            random_next = [random.choice(next_words)]
            # if get_character_count(line+random_next) < 124:
            line += random_next

    else:
        while line[-1][-1] not in line_enders:
            next_words = markov_chain[tuple(line[-2:])]
            line += [random.choice(next_words)]

    return ' '.join(line)


def generate_paragraph(markov_chain, lines=3):
    paragraph = generate_line(markov_chain)

    for i in range(lines - 1):
        paragraph += generate_line(markov_chain)
        paragraph += ' '

    return paragraph


def generate_article():
    title_str, description_str = get_title_and_description()
    # title_chain = make_markov_chain(title_str)
    description_chain = make_markov_chain(description_str)
    # title = generate_line(title_chain, title=True)
    # description = generate_paragraph(description_chain, 1)
    twitter = generate_line(description_chain, twitter=True)


def get_tweet():
    title_str, description_str = get_title_and_description()
    description_chain = make_markov_chain(description_str)
    tweet = generate_line(description_chain, twitter=True) + ' #MarkovScience'

    while get_character_count(tweet) > 140:
        tweet = generate_line(
            description_chain, twitter=True) + ' #MarkovScience'

    print tweet
    return tweet


def tweet():
    tweet = get_tweet()
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)
    api = tweepy.API(auth)

    api.update_status(tweet)


if __name__ == '__main__':
    tweet()
