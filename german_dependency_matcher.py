#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Jana Meier

from spacy.matcher import DependencyMatcher

hits = {}


def get_extension(doc, head_id, dependency):
    """Gets compound words and particles of phrasal verbs.

    All subjects and objects are checked for compound words such as names (e.g. Lisa Maria Müller) and all verbs are
    checked for particles so that particle verbs can be detected (e.g. aufstehen --> er steht auf). The input is the
    index of the noun or verb, which is the head of a compound words resp. of a particle. The output is either a list
    with the index of the found compound/particle together with their head or simply None if nothing is found.

    :param doc: the entire text to analyse
    :param head_id: either the noun (subj or obj) or the verb which the compound word or the particle depends on
    :param dependency: either "pnc" or "svp"

    :input: 1
    :return: [0, 1]
    """
    compound_ids = [c.i for c in doc[head_id].children if c.dep_ == dependency]
    if compound_ids:
        return sorted(compound_ids + [head_id])
    else:
        return None


def get_compounds_and_particles(doc, token_ids, subj_idx, verb_idx, obj_idx):
    """Checks if the matched pattern is already in the dictionary. If not the function returns the matched pattern
    together with the noun compounds and the particles.

    :param doc: the entire text to be analysed
    :param token_ids: the indexes of S, V and O
    :param subj_idx: the index/position of the subject in the token ids
    :param verb_idx: the index/position of the verb in the token ids
    :param obj_idx: the index/position of the object in the token ids

    :input:  [2, 1, 4]
    :return: (2, 1, 4) [0, 1] None None
    """
    ids = tuple(token_ids)
    compound_subj = get_extension(doc, ids[subj_idx], "pnc")
    phrasal = get_extension(doc, ids[verb_idx], "svp")
    compound_obj = get_extension(doc, ids[obj_idx], "pnc")

    if not ids in hits:
        return ids, compound_subj, phrasal, compound_obj


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
            "RIGHT_ATTRS": {"DEP": "sb"}
        },
        {
            "LEFT_ID": "svo_verb",
            "REL_OP": ">",
            "RIGHT_ID": "svo_object",
            "RIGHT_ATTRS": {"DEP": "oa"}
        }
    ]

    pattern_aux_as_fullverb = [
        {
            "RIGHT_ID": "svo_verb",
            "RIGHT_ATTRS": {"POS": "AUX"}
        },
        {
            "LEFT_ID": "svo_verb",
            "REL_OP": ">",
            "RIGHT_ID": "svo_subject",
            "RIGHT_ATTRS": {"DEP": "sb"}
        },
        {
            "LEFT_ID": "svo_verb",
            "REL_OP": ">",
            "RIGHT_ID": "svo_object",
            "RIGHT_ATTRS": {"DEP": "oa"}
        }
    ]

    pattern_auxiliary = [
        {
            "RIGHT_ID": "svo_verb_aux",
            "RIGHT_ATTRS": {"POS": "AUX"}
        },
        {
            "LEFT_ID": "svo_verb_aux",
            "REL_OP": ">",
            "RIGHT_ID": "svo_subject",
            "RIGHT_ATTRS": {"DEP": "sb"}
        },
        {
            "LEFT_ID": "svo_verb_aux",
            "REL_OP": ">",
            "RIGHT_ID": "svo_verb",
            "RIGHT_ATTRS": {"DEP": "oc"}
        },
        {
            "LEFT_ID": "svo_verb",
            "REL_OP": ">",
            "RIGHT_ID": "svo_object",
            "RIGHT_ATTRS": {"DEP": "oa"}
        }
    ]

    pattern_passive = [
        {
            "RIGHT_ID": "passive_verb_aux",
            "RIGHT_ATTRS": {"Lemma": "werden"}
        },
        {
            "LEFT_ID": "passive_verb_aux",
            "REL_OP": ">>",
            "RIGHT_ID": "passive_subject",
            "RIGHT_ATTRS": {"DEP": "sb"}
        },
        {
            "LEFT_ID": "passive_verb_aux",
            "REL_OP": ">>",
            "RIGHT_ID": "passive_verb",
            "RIGHT_ATTRS": {"DEP": "oc"}
        },
        {
            "LEFT_ID": "passive_verb",
            "REL_OP": ">>",
            "RIGHT_ID": "passive_präp",
            "RIGHT_ATTRS": {"Lemma": "von"}
        },
        {
            "LEFT_ID": "passive_präp",
            "REL_OP": ">",
            "RIGHT_ID": "passive_obj",
            "RIGHT_ATTRS": {"DEP": "nk"}
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
            "RIGHT_ATTRS": {"DEP": "sb"}
        },
        {
            "LEFT_ID": "ellip_verb",
            "REL_OP": ">>",
            "RIGHT_ID": "ellip_verb_2",
            "RIGHT_ATTRS": {"DEP": "cj"}
        },
        {
            "LEFT_ID": "ellip_verb_2",
            "REL_OP": ">",
            "RIGHT_ID": "ellip_obj_2",
            "RIGHT_ATTRS": {"DEP": "oa"}
        }
    ]

    ###################################################################################################################

    def svo_match(matcher, doc, id, matches):
        """Callback function to act on matches. In this case on SVO matches.

        :param matcher: Dependency Matcher
        :param doc: The entire document to be analysed
        :param id: The ID of the particular pattern
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

        # get compound nouns and phrasal verbs
        ids, compound_subj, phrasal_verb, compound_obj = get_compounds_and_particles(doc, token_ids, 1, 0, 2)

        # add pattern name, S, V, O to the dictionary
        hits[ids] = {'pattern_name': nlp.vocab[match_id].text, 'S': ids[1], 'V': ids[0], 'O': ids[2]}

        # if available add also compound nouns and phrasal verbs
        if compound_subj:
            hits[ids]['CS'] = compound_subj
        if phrasal_verb:
            hits[ids]['PV'] = phrasal_verb
        if compound_obj:
            hits[ids]['CO'] = compound_obj

    def auxiliary_match(matcher, doc, id, matches):
        """Callback function to act on matches. In this case on auxiliary matches.

        :param matcher: Dependency Matcher
        :param doc: The entire document to be analysed
        :param id: The ID of the particular pattern
        :param matches: the matches of the specified patterns which consist of a list containing (match_id, token_ids)
        tuples
        """
        single_match = matches[id]
        match_id, token_ids = single_match
        svo_verb_aux, svo_subject, svo_verb, svo_object = token_ids

        ids, compound_subj, phrasal_verb, compound_obj = get_compounds_and_particles(doc, token_ids, 1, 2, 3)
        # get rid of the index of the auxiliary verb
        updated_id = ids[1:]

        hits[updated_id] = {'pattern_name': nlp.vocab[match_id].text, 'S': ids[1], 'V': ids[2], 'O': ids[3]}

        if compound_subj:
            hits[updated_id]['CS'] = compound_subj
        if phrasal_verb:
            hits[updated_id]['PV'] = phrasal_verb
        if compound_obj:
            hits[updated_id]['CO'] = compound_obj

    def passive_match(matcher, doc, id, matches):
        """Callback function to act on matches. In this case on passive matches.

        :param matcher: Dependency Matcher
        :param doc: The entire document to be analysed
        :param id: The ID of the particular pattern
        :param matches: the matches of the specified patterns which consist of a list containing (match_id, token_ids)
        tuples
        """

        single_match = matches[id]
        match_id, token_ids = single_match
        passive_verb_aux, svo_subject, svo_verb, passive_prep, svo_object = token_ids

        ids, compound_subj, phrasal_verb, compound_obj = get_compounds_and_particles(doc, token_ids, 1, 2, 4)

        # get rid of the index of the preposition 'von' and auxiliary 'werden', only index of S, V and O is relevant.
        added_span = ids[1:3]
        added_value = (ids[4],)

        updated_id = added_span + added_value

        hits[updated_id] = {'pattern_name': nlp.vocab[match_id].text, 'S': ids[4], 'V': ids[2], 'O': ids[1]}

        if compound_subj:
            hits[updated_id]['CS'] = compound_subj
        if phrasal_verb:
            hits[updated_id]['PV'] = phrasal_verb
        if compound_obj:
            hits[updated_id]['CO'] = compound_obj

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

        subject = [c.i for c in doc[svo_verb_2].children if c.dep_ == 'sb']

        # if the second verb has a subject, ignore this case.
        if subject:
            pass
        else:
            ids, compound_subj, phrasal_verb, compound_obj = get_compounds_and_particles(doc, token_ids, 1, 2, 3)
            # get rid of the first verb and object that the dependency matcher has matched.
            added_value = (ids[1],)
            added_span = ids[2:4]

            updated_id = added_value + added_span

            hits[updated_id] = {'pattern_name': nlp.vocab[match_id].text, 'S': ids[1], 'V': ids[2], 'O': ids[3]}
            if compound_subj:
                hits[updated_id]['CS'] = compound_subj
            if phrasal_verb:
                hits[updated_id]['PV'] = phrasal_verb
            if compound_obj:
                hits[updated_id]['CO'] = compound_obj

            ###########################################################################################################
            # Check if there is a second elliptical subject

            # check if there is a verb depending on the second verb
            ids1 = [c.i for c in doc[svo_verb_2].children if c.pos_ == 'VERB']
            if ids1:
                token_ids.append(ids1[0])
                # check if this verb has a subject, if yes, skip this case
                ids2 = [c.i for c in doc[token_ids[-1]].children if c.dep_ == 'sb']
                if ids2:
                    pass
                else:
                    # check whether the verb has a direct object
                    ids3 = [c.i for c in doc[token_ids[-1]].children if c.dep_ == 'oa']
                    if ids3:
                        token_ids.append(ids3[0])
                        ids, compound_subj, phrasal_verb, compound_obj = get_compounds_and_particles(doc, token_ids, 1,
                                                                                                     4, 5)

                        added_value = (ids[1],)
                        added_span = ids[4:6]
                        updated_id = added_value + added_span

                        hits[updated_id] = {'pattern_name': nlp.vocab[match_id].text, 'S': ids[1], 'V': ids[4],
                                            'O': ids[5]}
                        if compound_subj:
                            hits[updated_id]['CS'] = compound_subj
                        if phrasal_verb:
                            hits[updated_id]['PV'] = phrasal_verb
                        if compound_obj:
                            hits[updated_id]['CO'] = compound_obj

    ###################################################################################################################
    matcher.add("SVO", [pattern_svo], on_match=svo_match)
    matcher.add("aux_as_fullverb", [pattern_aux_as_fullverb], on_match=svo_match)
    matcher.add("auxiliary", [pattern_auxiliary], on_match=auxiliary_match)
    matcher.add("passive", [pattern_passive], on_match=passive_match)
    matcher.add("elliptical_subject", [pattern_elliptical_subject], on_match=elliptical_match)

    matcher(doc)

    return hits