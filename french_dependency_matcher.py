#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Jana Meier

from spacy.matcher import DependencyMatcher

hits = {}


def get_extension(doc, head_id, dependency):
    """Gets compound words.

    All subjects and objects are checked for compound words such as names (e.g. Lisa Maria Müller). The input is the
    index of the noun, which is the head of a compound words. The output is either a list with the index of
    the found compound together with their head or simple None if nothing is found.

    :param doc: the entire text to be analysed
    :param head_id: either the noun (subj or obj) which the compound word depends on
    :param dependency: either "compound"

    :input: 1
    :return: [0, 1]
    """
    compound_ids = [c.i for c in doc[head_id].children if c.dep_ == dependency]
    if compound_ids:
        return sorted(compound_ids + [head_id])
    else:
        return None


def get_compounds(nlp, doc, match_id, token_ids, svo_subject, subj_idx, svo_object, obj_idx):
    """Checks if the matched pattern is already in the dictionary. If not the function returns the matched pattern
    together with the noun compounds.


    :param doc: the entire text to be analysed
    :param match_id: the id of the match
    :param token_ids: the indexes of S, V and O
    :param svo_subject: the index of the subject in the text
    :param subj_idx: the index of the subject in the token ids
    :param svo_object: the index of the object in the text
    :param obj_idx: the index of the object in the token ids

    :input:  [2, 1, 4]
    :return: (2, 1, 4) [0, 1] None None
    """

    ids = tuple(token_ids)
    compound_subj = get_extension(doc, ids[subj_idx], "flat:name")
    compound_obj = get_extension(doc, ids[obj_idx], "flat:name")

    if not ids in hits:
        # print(nlp.vocab[match_id].text, '\n', doc[svo_subject].text, compound_subj,
        #      doc[svo_object].text, compound_obj)
        return ids, compound_subj, compound_obj


def update_svo_triplets_from_sentence(nlp, doc):
    """Parses through the text and matches the specified patterns.

    The sentences with a matched pattern are sent to their respective functions and then added to the global
    variable "hits" ("hits" dictionary gets updated).
    :param nlp: the spacy language pipeline
    :param doc: the entire text to be analysed
    """

    matcher = DependencyMatcher(nlp.vocab)

    pattern_svo = [
        {
            "RIGHT_ID": "svo_verb",
            "RIGHT_ATTRS": {"POS": "VERB"}
        },
        {
            "LEFT_ID": "svo_verb",
            "REL_OP": ">",
            "RIGHT_ID": "svo_subject",
            "RIGHT_ATTRS": {"DEP": "nsubj"}
        },
        {
            "LEFT_ID": "svo_verb",
            "REL_OP": ">",
            "RIGHT_ID": "svo_object",
            "RIGHT_ATTRS": {"DEP": "obj"}
        }
    ]

    pattern_participle_present = [
        {
            "RIGHT_ID": "svo_subject",
            "RIGHT_ATTRS": {"POS": "NOUN"}
        },
        {
            "LEFT_ID": "svo_subject",
            "REL_OP": ">",
            "RIGHT_ID": "svo_verb",
            "RIGHT_ATTRS": {"DEP": "acl"}
        },
        {
            "LEFT_ID": "svo_verb",
            "REL_OP": ">",
            "RIGHT_ID": "svo_object",
            "RIGHT_ATTRS": {"DEP": "obj"}
        }
    ]

    pattern_passive = [
        {
            "RIGHT_ID": "passive_verb",
            "RIGHT_ATTRS": {"POS": "VERB"}
        },
        {
            "LEFT_ID": "passive_verb",
            "REL_OP": ">",
            "RIGHT_ID": "passive_subject",
            "RIGHT_ATTRS": {"DEP": "nsubj:pass"}
        },
        {
            "LEFT_ID": "passive_verb",
            "REL_OP": ">",
            "RIGHT_ID": "passive_obj",
            "RIGHT_ATTRS": {"DEP": "obl:agent"}
        },
        {
            "LEFT_ID": "passive_obj",
            "REL_OP": ">",
            "RIGHT_ID": "passive_agent",
            "RIGHT_ATTRS": {"DEP": "case"}
        }
    ]

    pattern_elliptical_subject = [
        {
            "RIGHT_ID": "ellip_verb",
            "RIGHT_ATTRS": {"POS": "VERB"}
        },
        {
            "LEFT_ID": "ellip_verb",
            "REL_OP": ">",
            "RIGHT_ID": "ellip_subj",
            "RIGHT_ATTRS": {"DEP": "nsubj"}
        },
        {
            "LEFT_ID": "ellip_verb",
            "REL_OP": ">",
            "RIGHT_ID": "ellip_verb_2",
            "RIGHT_ATTRS": {"DEP": "conj"}
        },
        {
            "LEFT_ID": "ellip_verb_2",
            "REL_OP": ">",
            "RIGHT_ID": "ellip_obj_2",
            "RIGHT_ATTRS": {"DEP": "obj"}
        }
    ]

    ###################################################################################################################

    def svo_match(matcher, doc, id, matches):
        """Callback function to act on matches. In this case on SVO matches.

        :param matcher: Dependency Matcher.
        :param doc: The entire document to be analysed.
        :param id: The ID of the particular pattern.
        :param matches: the matches of the specified patterns which consist of a list containing (match_id, token_ids)
        tuples
        """
        # single_match is the specific match out of the list of all matches of the document.
        single_match = matches[id]
        # the two parts of the tuples of a single match, the first one containing the match_id and the second one token
        # ids, the indexes for S,V,O
        match_id, token_ids = single_match
        # further specification which of the indexes is the verb, subject and object.
        svo_verb, svo_subject, svo_object = token_ids

        # get compound nouns
        ids, compound_subj, compound_obj = get_compounds(nlp, doc, match_id, token_ids, svo_subject, 1, svo_object, 2)

        # add pattern name, S, V, O to the dictionary
        hits[ids] = {'pattern_name': nlp.vocab[match_id].text, 'S': ids[1], 'V': ids[0], 'O': ids[2]}

        # if available add also compound nouns
        if compound_subj:
            hits[ids]['CS'] = compound_subj
        if compound_obj:
            hits[ids]['CO'] = compound_obj

    def participle_match(matcher, doc, id, matches):
        """Callback function to act on matches. In this case on participle present matches.

        example: Je lis un roman racontant la vie d’un médecin.

        :param matcher: Dependency Matcher.
        :param doc: The entire document to be analysed.
        :param id: The ID of the particular pattern.
        :param matches: the matches of the specified patterns which consist of a list containing (match_id, token_ids)
        tuples
        """
        # single_match is the specific match out of the list of all matches of the document.
        single_match = matches[id]
        # the two parts of the tuples of a single match, the first one containing the match_id and the second one token
        # ids, the indexes for S,V,O
        match_id, token_ids = single_match
        # further specification which of the indexes is the verb, subject and object.
        svo_subject, svo_verb, svo_object = token_ids

        # get compound nouns
        ids, compound_subj, compound_obj = get_compounds(nlp, doc, match_id, token_ids, svo_subject, 0, svo_object, 2)

        # add pattern name, S, V, O to the dictionary
        hits[ids] = {'pattern_name': nlp.vocab[match_id].text, 'S': ids[1], 'V': ids[0], 'O': ids[2]}

        # if available add also compound nouns
        if compound_subj:
            hits[ids]['CS'] = compound_subj
        if compound_obj:
            hits[ids]['CO'] = compound_obj

    def passive_match(matcher, doc, id, matches):
        """Callback function to act on matches. In this case on passive matches.

        :param matcher: Dependency Matcher.
        :param doc: The entire document to be analysed.
        :param id: The ID of the particular pattern.
        :param matches: the matches of the specified patterns which consist of a list containing (match_id, token_ids)
        tuples
        """
        single_match = matches[id]
        match_id, token_ids = single_match
        svo_verb, svo_object, svo_subject, svo_prep = token_ids

        ids, compound_subj, compound_obj = get_compounds(nlp, doc, match_id, token_ids, svo_subject, 2, svo_object, 1)

        # get rid of the index of the preposition 'by', only index of S, V and O is relevant.
        id = ids[:3]

        hits[id] = {'pattern_name': nlp.vocab[match_id].text, 'S': ids[2], 'V': ids[0], 'O': ids[1]}

        if compound_subj:
            hits[id]['CS'] = compound_subj
        if compound_obj:
            hits[id]['CO'] = compound_obj

    def elliptical_match(matcher, doc, id, matches):
        """Callback function to act on matches. In this case on elliptical subject.

        :param matcher: Dependency Matcher.
        :param doc: The entire document to be analysed.
        :param id: The ID of the particular pattern.
        :param matches: the matches of the specified patterns which consist of a list containing (match_id, token_ids)
        tuples
        """

        single_match = matches[id]
        match_id, token_ids = single_match
        svo_verb_1, svo_subject, svo_verb_2, svo_object_2 = token_ids

        ###############################################################################################################
        # Check if there is one elliptical subject

        subject = [c.i for c in doc[svo_verb_2].children if c.dep_ == 'nsubj']

        # if the second verb has a subject, ignore this case.
        if subject:
            pass
        else:
            ids, compound_subj, compound_obj = get_compounds(nlp, doc, match_id, token_ids, svo_subject, 1,
                                                             svo_object_2, 3)
            # get rid of the first verb.
            id = (ids[1:4])

            hits[id] = {'pattern_name': nlp.vocab[match_id].text, 'S': ids[1], 'V': ids[2], 'O': ids[3]}
            if compound_subj:
                hits[id]['CS'] = compound_subj
            if compound_obj:
                hits[id]['CO'] = compound_obj

            ###########################################################################################################
            # Check if there is a second elliptical subject

            # check if there is a verb depending on the second verb
            ids1 = [c.i for c in doc[svo_verb_2].children if c.pos_ == 'VERB']
            if ids1:
                token_ids.append(ids1[0])
                # check if this verb has a subject, if yes, skip this case
                ids2 = [c.i for c in doc[token_ids[-1]].children if c.dep_ == 'nsubj']
                if ids2:
                    pass
                else:
                    # check whether the verb has a direct object
                    ids3 = [c.i for c in doc[token_ids[-1]].children if c.dep_ == 'dobj']
                    if ids3:
                        token_ids.append(ids3[0])
                        ids, compound_subj, compound_obj = get_compounds(doc, match_id, token_ids, svo_subject, 1,
                                                                         token_ids[-1], 5)

                        added_value = (ids[1],)
                        added_span = ids[4:6]
                        id = added_value + added_span

                        hits[id] = {'pattern_name': nlp.vocab[match_id].text, 'S': ids[1], 'V': ids[4], 'O': ids[5]}
                        if compound_subj:
                            hits[id]['CS'] = compound_subj
                        if compound_obj:
                            hits[id]['CO'] = compound_obj

    ###################################################################################################################
    matcher.add("SVO", [pattern_svo], on_match=svo_match)
    #matcher.add("participle_present", [pattern_participle_present], on_match=participle_match)
    matcher.add("passive", [pattern_passive], on_match=passive_match)
    #matcher.add("elliptical_subject", [pattern_elliptical_subject], on_match=elliptical_match)

    matcher(doc)

    return hits
