# markov chain title and description generator from SHARE results

import sys
import getopt
import random

import tweepy
import requests

import settings

OSF_URL = 'https://osf.io/api/v1/share/?q={}&size=250&start={}'


def get_title_and_description(q, pages):
    ''' Goes to the SHARE API endpoint and grab some pages
    of text from title description, and returns a string
    '''
    title = ''
    description = ''
    start = 0
    for page in range(0, int(pages)):
        print(OSF_URL.format(q, start))
        items = requests.get(OSF_URL.format(q, start), verify=False)

        page_text = items.json()
        results = page_text['results']

        for item in results:
            description += item['description'] + ' '
            title += item['title'] + ' '

        start += 250

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
            next_words = markov_chain[tuple(line[-2:])]
            random_next = [random.choice(next_words)]
            line += random_next

    else:
        while line[-1][-1] not in line_enders:
            next_words = markov_chain[tuple(line[-2:])]
            line += [random.choice(next_words)]

    return ' '.join(line)


def get_tweet(q, pages):
    title_str, description_str = get_title_and_description(q, pages)
    description_chain = make_markov_chain(description_str)
    tweet = generate_line(description_chain, twitter=True) + ' #MarkovScience'

    while get_character_count(tweet) > 140:
        tweet = generate_line(
            description_chain, twitter=True) + ' #MarkovScience'

    print(tweet)
    return tweet


def tweet(q='*', pages=1):
    tweet = get_tweet(q, pages)
    auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)
    api = tweepy.API(auth)

    api.update_status(tweet)


def usage():
    print('Usage:')
    print('-q or --query: enter a search query, defaults to *')
    print('-p or --pages: enter the number of pages to iterate over, defaults to 1')


def main(argv):
    q = '*'
    pages = 1
    try:
        options, args = getopt.getopt(argv, "hq:p:", ["help", "query=", "pages="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for option, arg in options:
        if option in ("-h", "--help"):
            usage()
            sys.exit()
        elif option in ("-q", "--query"):
            q = arg
        elif option in ("-p", "--pages"):
            pages = arg

    tweet(q, pages)


if __name__ == '__main__':
    main(sys.argv[1:])
