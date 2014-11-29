# markov chain title and description generator from SHARE results

import random

import requests

OSF_URL = 'http://share-dev.osf.io/api/v1/app/6qajn/?page:{}'


def get_title_and_description(pages=10):
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
            description += item['description']
            title += item['title']

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


def generate_line(markov_chain):
    ''' Takes a dict of markov chains and returns random text!'''

    start = ' '
    while not start[0][0].isupper():
        start = random.choice(markov_chain.keys())

    line = list(start)

    line_enders = ['?', '.', '!', '\n  ']

    while line[-1][-1] not in line_enders:
        next_words = markov_chain[tuple(line[-2:])]
        line += [random.choice(next_words)]
        # line += ' '

    return ' '.join(line)


def generate_paragraph(markov_chain, lines=3):
    paragraph = generate_line(markov_chain)

    for i in range(lines - 1):
        paragraph += generate_line(markov_chain)

    return paragraph


def fix_title(line):
    title = line
    for word in line.split():
        if word[0].islower() and word != word.upper() and word != word.lower():
            for letter in word:
                if letter.isupper():
                    title_index = line.index(word)
                    title = line[:title_index]
                    import pdb; pdb.set_trace()

    return title


def generate_article():
    title_str, description_str = get_title_and_description()
    title_chain = make_markov_chain(title_str)
    description_chain = make_markov_chain(description_str)
    long_title = generate_line(title_chain)
    title = fix_title(long_title)
    description = generate_paragraph(description_chain, 2)

    print(title)
    print('------')
    print(description)


if __name__ == '__main__':
    generate_article()
