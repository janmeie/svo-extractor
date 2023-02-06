#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Jana Meier

from argparse import ArgumentParser
from smart_open import open
import spacy
import json
from dependency_utils import read_input, get_token_and_lemma_and_pos, get_unique_triplets, process_dataframe


def get_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(description='A commandline tool for parsing newspapers articles')
    parser.add_argument('input_file',
                        help="input file name",
                        type=str)
    parser.add_argument('--input_format',
                        help='process an individual text or a data frame with several texts',
                        choices=('indtxt', 'datafr'),
                        default='indtxt')
    parser.add_argument('language',
                        help='the language',
                        choices=('en', 'fr', 'es', 'it', 'de'))
    parser.add_argument('--pipeline',
                        help='the spacy language pipeline size, sm or md',
                        choices=('sm', 'md'),
                        default='sm')
    parser.add_argument('--unique_triplets',
                        help='if present, prints the unique lemmas of all the triplets found in the text',
                        action='store_true')
    parser.add_argument('--nr_unique_triplets',
                        help='if presents, prints the number of unique triplets found in the text',
                        action='store_true')
    parser.add_argument('--print', '-p',
                        help='if present, prints the svo dictionary to the std output',
                        action='store_true')
    parser.add_argument('--output_file',
                        help="output file name",
                        type=str,
                        default='svo_triplets_output.jsonl.bz2')
    return parser


def main():
    # Parse console arguments
    parser = get_argument_parser()
    args = parser.parse_args()

    # Choose language
    if args.language == 'en':
        from english_dependency_matcher import update_svo_triplets_from_sentence
    elif args.language == 'fr':
        from french_dependency_matcher import update_svo_triplets_from_sentence
    elif args.language == 'es':
        from spanish_dependency_matcher import update_svo_triplets_from_sentence
    elif args.language == 'it':
        from italian_dependency_matcher import update_svo_triplets_from_sentence
    elif args.language == 'de':
        from german_dependency_matcher import update_svo_triplets_from_sentence

    # Choose language and pipeline
    if args.language == 'en' and args.pipeline == 'md':
        nlp = spacy.load('en_core_web_md')
    elif args.language == 'en':
        nlp = spacy.load('en_core_web_sm')
    elif args.language == 'fr' and args.pipeline == 'md':
        nlp = spacy.load('fr_core_news_md')
    elif args.language == 'fr':
        nlp = spacy.load('fr_core_news_sm')
    elif args.language == 'es' and args.pipeline == 'md':
        nlp = spacy.load('es_core_news_md')
    elif args.language == 'es':
        nlp = spacy.load('es_core_news_sm')
    elif args.language == 'it' and args.pipeline == 'md':
        nlp = spacy.load('it_core_news_md')
    elif args.language == 'it':
        nlp = spacy.load('it_core_news_sm')
    elif args.language == 'de' and args.pipeline == 'md':
        nlp = spacy.load('de_core_news_md')
    elif args.language == 'de':
        nlp = spacy.load('de_core_news_sm')

    # Process the input file
    if args.input_format == 'datafr':
        process_dataframe(args.input_file, nlp, update_svo_triplets_from_sentence, args, args.output_file)
    else:
        text_string = read_input(args.input_file)
        doc = nlp(text_string)
        hits_dictionary = update_svo_triplets_from_sentence(nlp, doc)

        get_token_and_lemma_and_pos(hits_dictionary, doc)
        unique_triplets, nr_unique_triplets = get_unique_triplets(list(hits_dictionary.values()))

        if args.unique_triplets:
            print(unique_triplets)

        if args.nr_unique_triplets:
            print(nr_unique_triplets)

        svo_dict = {'svo_triplets': list(hits_dictionary.values()), 'meta_data': [], 'legth_text': len(doc),
                    'nr_verbs': len([c for c in doc if c.pos_ == "VERB"]), 'unique_triplets': unique_triplets,
                    'nr_unique_triplets': nr_unique_triplets}

        if args.print:
            print(svo_dict)

        # write output file
        with open(args.output_file, 'w', encoding='utf-8') as outfile:
            print(json.dumps(svo_dict, ensure_ascii=False), file=outfile)


if __name__ == '__main__':
    main()
