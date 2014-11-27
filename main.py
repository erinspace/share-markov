# markov chain title and description generator from SHARE results

import random

import requests

OSF_URL = 'http://share-dev.osf.io/api/v1/app/6qajn/?page:{}'


def get_string(pages=10):
    ''' Goes to the SHARE API endpoint and grab some pages
    of text from description, and returns a string
    '''
    text = ''
    for page in range(0, pages):
        items = requests.get(OSF_URL.format(page), verify=False)

        page_text = items.json()
        results = page_text['results']

        for item in results:
            text += item['description']

    return text


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


def generate_line(markov_chain):
    ''' Takes a dict of markov chains and returns random text!'''

    start = ' '
    while not start[0][0].isupper():
        start = random.choice(markov_chain.keys())

    line = list(start)

    line_enders = ['?', '.', '!']

    while line[-1][-1] not in line_enders:
        next_words = markov_chain[tuple(line[-2:])]
        line += [random.choice(next_words)]

    return ' '.join(line)


def generate_paragraph(markov_chain, lines=3):
    paragraph = generate_line(markov_chain)

    for i in range(lines - 1):
        paragraph += generate_line(markov_chain)

    return paragraph


def generate_title(markov_chain):
    title = list(random.choice(markov_chain.keys()))

    title_enders = ['?', '.', '!', ',']

    while title[-1][-1] not in title_enders:
        next_words = markov_chain[tuple(title[-2:])]
        title += [random.choice(next_words)]

    return ' '.join(title[:-1]).title()


if __name__ == '__main__':
    text = get_string()
    markov_chain = make_markov_chain(text)
    line = generate_line(markov_chain)
    paragraph = generate_paragraph(markov_chain, 5)
    title = generate_title(markov_chain)
    print(line)
