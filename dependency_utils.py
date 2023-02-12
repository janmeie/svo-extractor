#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Jana Meier

from smart_open import open
import pandas as pd
import json


def read_input(filename: str) -> str:
    """Reads in a file.

    Returns the text as a string without line breaks.
    :param filename: name of input file
    :return: text as string without line breaks
    """
    string_without_line_breaks = ""
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            stripped_line = line.replace('\n', ' ')
            string_without_line_breaks += stripped_line
        file.close()

    return string_without_line_breaks


def update_token_lemma_pos(svo_dict, doc):
    """Adds tokens, lemmas and pos tags to each word of the SVO triplet.

    expands the svo_dict with tokens, lemmas and pos tags for each word of the triplet.
    Returns the same dictionary, but enriched.

    :param svo_dict: the dictionary to be expanded with tokens, lemmas and pos tags.
    :param doc: the entire text.

    :input: {'CS': [27, 28, 29], 'S': 29, 'V': 30, 'PV': [30, 31], 'O': 32}
    :return: {'CS': [27, 28, 29], 'S': 29, 'V': 30, 'PV': [30, 31], 'O': 32,
            'CS_tokens': ['Luisa', 'Maria', 'Müller'], ...
            'CS_lemmas': ['Luisa','Maria', 'Müller'], ...
            'CS_pos': ['PROPN', 'PROPN', 'PROPN'], ... }
    """
    print(svo_dict)
    for key in list(svo_dict):
        if key == 'pattern_name':
            continue
        else:
            token_key = key + '_token'
            lemma_key = key + '_lemma'
            pos_key = key + '_pos'
            keyvalue = svo_dict[key]

            # if the svo_dict value is an integer and no list
            if type(keyvalue) == int:
                token_value = doc[keyvalue].text
                svo_dict[token_key] = token_value
                lemma_value = doc[keyvalue].lemma_
                svo_dict[lemma_key] = lemma_value
                pos_value = doc[keyvalue].pos_
                svo_dict[pos_key] = pos_value

            # if the svo_dict value is a list
            elif type(keyvalue) == list:
                token_values = [doc[i].text for i in keyvalue]
                svo_dict[token_key] = token_values
                lemma_values = [doc[i].lemma_ for i in keyvalue]
                svo_dict[lemma_key] = lemma_values
                pos_values = [doc[i].pos_ for i in keyvalue]
                svo_dict[pos_key] = pos_values

            else:
                svo_dict[token_key] = None
                svo_dict[lemma_key] = None
                svo_dict[pos_key] = None


def get_token_and_lemma_and_pos(dictionary, doc):
    """separates the index tuples (key) from the SVO indexes (value).

    :param dictionary: the dictionary with the index tuples as keys and the SVO triplets with their indexes as values
    :param doc: the entire text

    :input: {(1, 0, 3): {'S': 0, 'V': 1, 'O': 3}, (8, 7, 10): {'CS': [5, 6, 7], 'S': 7, 'V': 8, 'O': 10},
    (19, 17, 21): {'S': 17, 'V': 19, 'PV': [19, 20], 'O': 21}, (30, 29, 32): {'CS': [27, 28, 29], 'S': 29, 'V': 30,
    'PV': [30, 31], 'O': 32}}

    :return: {'S': 0, 'V': 1, 'O': 3}, {'CS': [5, 6, 7], 'S': 7, 'V': 8, 'O': 10},
    {'S': 17, 'V': 19, 'PV': [19, 20], 'O': 21}, {'CS': [27, 28, 29], 'S': 29, 'V': 30, 'PV': [30, 31], 'O': 32}
    """
    for key, value in dictionary.items():
        update_token_lemma_pos(value, doc)


def get_unique_triplets(hits_list):
    """gets unique triplets.

    Returns a list with all the unique triplets and the total number of unique triplets per text.
    :param hits_list: list with dictionaries containing SVO triplets. It is possible that the same triplet appears
    several time in the dictionary, all SVO duplicates get deleted.
    :return: list with unique SVO triplets and the total number of unique triplets found
    """

    def check_extension(extension):
        """checks if the verb is a phrasal verb and if the noun is a compound word.

        Returns either the extension or an empty string.
        :param extension: the dictionary keys "CS_lemma" or "PV_lemma"
        :return: if the key "CS_lemma" or "PV_lemma" is available, its corresponding value gets returned, if not
        an empty string is returned.
        """
        key = extension
        if key in hits_dict:
            return hits_dict[key]
        else:
            return ''

    svo_list = []

    for hits_dict in hits_list:
        svo_string = str(hits_dict['S_lemma']) + str(check_extension('CS_lemma')) + '_' + \
                     hits_dict['V_lemma'] + str(check_extension('PV_lemma')) + '_' + hits_dict['O_lemma'] + \
                     str(check_extension('CO_lemma'))
        svo_list.append(svo_string)
    unique_svo_triplets = set(svo_list)
    unique_svo_triplets_list = list(unique_svo_triplets)
    return unique_svo_triplets_list, len(unique_svo_triplets_list)


def process_dataframe(input_file: str, nlp, update_svo_triplets_from_sentence, args, outfilename: str):
    """if the input is a dataframe the text is processed cell by cell and then printed to a json file

    :param input_file: name of the input file
    :param nlp: the spacy language pipeline: small or middle
    :param update_svo_triplets_from_sentence: the function from the respective language dependency matcher script
    :param args: the console arguments
    :param outfilename: name of the output file
    """
    new_df = pd.read_csv(input_file)

    with open(outfilename, 'w', encoding='utf-8') as outfile:
        for rowIndex, row in new_df.iterrows():
            doc = nlp(row['content'])
            hits_dictionary = update_svo_triplets_from_sentence(nlp, doc)
            get_token_and_lemma_and_pos(hits_dictionary, doc)
            unique_triplets, nr_unique_triplets = get_unique_triplets(list(hits_dictionary.values()))

            if args.unique_triplets:
                print(unique_triplets)

            if args.nr_unique_triplets:
                print(nr_unique_triplets)

            svo_dict = {'svo_triplets': list(hits_dictionary.values()),
                        'meta_data': {'publication_date': row.get('publication_date'),
                        'publication': row.get('publication'), 'topic': row.get('subject')},
                        'length_text': len(doc),
                        'nr_verbs': len([c for c in doc if c.pos_ == "VERB"]), 'unique_triplets': unique_triplets,
                        'nr_unique_triplets': nr_unique_triplets}

            if args.print:
                print(svo_dict)

            hits_dictionary.clear()
            print(json.dumps(svo_dict, ensure_ascii=False), file=outfile)
