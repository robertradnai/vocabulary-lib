"""
Follow learning progress and pick words based on it.

The goal of this module is to follow the learning progress of the user and to limit the number of words
the user is exposed to.

There are several groups:
    Not seen
    Actively learned: preferably about 5 words
    Recently learned: about 50 words
    Learned


The used data structure in this module is a list of lists (called status_dict)
{id_1:status_1, id_2: status_2, ..., id_n: status_n}

Maybe in update learning status? {group1: [id1, id2, id3], group2: [id4, id5, id6]}

Id identifies the word (key value for word_dict, status is a number that represents the learning status.
The words belong to groups. Where they belong changes based on good/bad answers.
There are 4 main categories: not seen, actively learning, recently learned, learned.
A possible config is that max. 5 words are shown in the actively learning group
and max. 50 words in the recently learned group.

First, if there aren't any seen words, 5 words are queued in the actively learning group.
If these are answered, the words from actively learning group go to the recently learned queue.
The vacancies from the actively learned group are filled from the not seen group.

In case of bad answers, you can get from learned to recently learned queue
and from recently learned to actively learning queue.


    Word groups and how they change based on the answers:
        - 1 not seen
             show flashcard
        - 2-3 actively learning (status 2-3) (5 words, 2 repetitions)
             good: active 1-->active 2
             bad: stays active 1
        - 4: actively learning (queued)
             not asked
        - 5-6: recently learned (50 words, 2 repetitions)
             bad: recent --> queued active
        - 7: recently learned (queued)
             not asked
        - 8: learned

    After every answer:
        - move words from recent queue to recent1 until recent1+2 is full or queue is empty
        - move words from active queue to active1 until active1+2 is full or queue is empty
        - move words from not seen to active until active1+2 is full or not seen is empty
"""

__docformat__ = 'reStructuredText'

import copy
import random
import logging
from .models import WordList
from typing import Dict

# Constants for the groups
NOTSEEN = 1
ACTIVE1 = 2
ACTIVE2 = 3
ACTIVEQ = 4
RECENT1 = 5
RECENT2 = 6
RECENTQ = 7
LEARNED = 8

DEFAULT_LEARNING_STATUS = 1

_CHANGEMAP_CORRECT = {NOTSEEN: ACTIVE1, ACTIVE1: RECENTQ,
                      ACTIVE2: RECENTQ, RECENT1: LEARNED,
                      RECENT2: LEARNED, LEARNED: LEARNED}
_CHANGEMAP_INCORRECT = {NOTSEEN: NOTSEEN, ACTIVE1: ACTIVE1,
                        ACTIVE2: ACTIVE1, RECENT1: ACTIVEQ,
                        RECENT2: RECENT1, LEARNED: RECENTQ}


def pick_word(learning_progress_dict: Dict[int, str], active_limit: int, recent_limit: int) -> (Dict[int, str], int):
    """Pick a random word based on current learning status
    :return: new learning progress dictionary, key of the picked word
    """

    progress_dict_mod = _fill_groups(
        _validate(learning_progress_dict),
        None,
        active_limit,
        recent_limit
    )
    # word_dict = _set_learning_status_dict(word_dict, progress_dict_mod)

    # Word that's being actively learned,
    # recently learned word or revise a learned word
    # Words from the not seen group are automatically moved to the being actively learned group
    sc = _group_status(progress_dict_mod)
    # At first, the same word in the active group should be asked 10% of the times
    # In the recently learned group, it should be about 1%
    # The recently learned group is in essence a dynamically changing "buffer"
    # Its size can be influenced only in an indirect way, by setting probabilities
    active_rows = sc.get(ACTIVE1, []) + sc.get(ACTIVE2, [])
    recent_rows = sc.get(RECENT1, []) + sc.get(RECENT2, [])
    learned_rows = sc.get(LEARNED, [])

    if len(active_rows) < 5:
        prob_active = 0.7
        prob_recent = 0.1
    elif len(recent_rows) < 40:
        # If there are not a lot of words in the rencently learned group,
        # the probability of asking them will be low
        prob_active = 0.45
        prob_recent = 0.35
    elif len(recent_rows) < 50:
        prob_active = 0.4
        prob_recent = 0.4
    else:
        prob_active = 0.3
        prob_recent = 0.5

    rnd = random.random()
    if rnd < prob_active:
        # Chance for picking a word from the active group
        if not len(active_rows) == 0:
            selected_key = random.choice(active_rows)
            logging.debug("Active group - picked {} from {}".format(selected_key, recent_rows))
        else:
            selected_key = random.choice(active_rows + recent_rows + learned_rows)
            logging.debug("Active group is empty - picked {} from {}".
                          format(selected_key, active_rows + recent_rows + learned_rows))
    elif prob_active < rnd < prob_active + prob_recent:
        # Chance for picking a word from the recent group
        if not len(recent_rows) == 0:
            selected_key = random.choice(recent_rows)
            logging.debug("Recent rows - picked {} from {}".format(selected_key, recent_rows))

        else:
            selected_key = random.choice(active_rows + recent_rows + learned_rows)
            logging.debug("Recent group is empty - picked {} from {}".
                          format(selected_key, active_rows + recent_rows + learned_rows))
    else:
        # Chance for picking a word from the learned group
        if not len(learned_rows) == 0:
            selected_key = random.choice(learned_rows)
            logging.debug("Learned rows - picked {} from {}".format(selected_key, learned_rows))
        else:
            selected_key = random.choice(active_rows + recent_rows + learned_rows)
            logging.debug("Learned group is empty - picked {} from {}".
                          format(selected_key, active_rows + recent_rows + learned_rows))

    return progress_dict_mod, selected_key


def submit_answer(learning_progress_dict, row_id, correct):
    """Check if answer is true, then modify learning status of the row in word_dict.
    :return: new learning progress dictionary
    """

    # Check if answer is true
    # Then modify learning status of the row of the asked word
    if correct:
        # Correct answer
        learning_progress_dict[row_id] = _CHANGEMAP_CORRECT[learning_progress_dict[row_id]]
    else:
        # Incorrect answer
        learning_progress_dict[row_id] = _CHANGEMAP_INCORRECT[learning_progress_dict[row_id]]

    # After modifying the row of the asked word, the word groups need to be rebalanced
    # (e. g. always 5 words being actively learned)
    # TODO move the part below
    # learning_status_dict_mod = _fill_groups(learning_status_dict, None, active_limit, recent_limit)

    return learning_progress_dict


def calculate_learning_progress(learning_status_dict: Dict[int, str]) -> float:
    """Calculate learning progress. Recently learned words count less weight
    and learned words count as 1 weight.

    :param learning_status_dict:
    :return:

    """
    groups = _group_status(learning_status_dict)
    all_count = sum([len(groups[key]) for key in groups])
    recent_count = len(groups.get(RECENT1, [])) + len(groups.get(RECENTQ, [])) + len(groups.get(RECENTQ, []))
    learned_count = len(groups.get(LEARNED, []))

    return (1*learned_count + 0.5*recent_count)/float(all_count)


def reset_progress(learning_status_dict: Dict[int, str]):
    return {row: NOTSEEN for row, value in learning_status_dict.items()}


def _validate(learning_progress: Dict[int, str]):
    return {key: _validate_learning_status(status) for key, status in learning_progress.items()}


def _validate_learning_status(learning_status, raise_exc=False):
    """Validate the learning progress field, return default if not defined or invalid.
    It needs to be executed only once, after importing the rows from an editable file.

    :param learning_status: content of the learning progress field
    :return: default or valid value of learnprog_field

    """
    if learning_status is None:
        if raise_exc:
            raise Exception("Improper entry in learning status field: {}".format(learning_status))
        return DEFAULT_LEARNING_STATUS
    elif type(learning_status) is not int:
        try:
            learning_status = int(learning_status)
        except (ValueError, TypeError):
            if raise_exc:
                raise Exception("Improper entry in learning status field: {}".format(learning_status))
            return DEFAULT_LEARNING_STATUS

    accepted_status = [NOTSEEN, ACTIVE1, ACTIVE2, ACTIVEQ, RECENT1, RECENT2, RECENTQ, LEARNED]

    if learning_status not in accepted_status:
        if raise_exc:
            raise Exception("Improper entry in learning status field: {}".format(learning_status))
        return DEFAULT_LEARNING_STATUS
    else:
        return learning_status


def _group_status(learning_status_dict):
    """Divide the row ids in status_list to groups based on learning status
    and shuffle the list elements so that when elements are chosen from the lists,
    then simply the first element can be chosen as a random element, it'll not be ordered)

    :param learning_status_dict:
    :return: {status1: [id1, id2, id3], status2: [id4, id5, id6]}

    """
    groups = {}
    for rowkey, status in learning_status_dict.items():
        # Append row id to an existing list or create a new list
        # if this status appears for the first time
        groups.setdefault(status, []).append(rowkey)
    for status in groups.keys():
        random.shuffle(groups[status])
    return groups


def _ungroup_status(grouped_learning_status):
    learning_status_dict = {}
    for group, rowkey_list in grouped_learning_status.items():
        for rowkey in rowkey_list:
            learning_status_dict[rowkey] = group
    return learning_status_dict


def _get_learning_groups_size(learning_status_dict):
    return {key: len(val) for key, val in learning_status_dict.items()}


def _fill_groups(status_dict, progress_marks, active_limit, recent_limit):
    """Regroup rows so that certain groups contain the specified number of items.

    :param status_dict:
    :param progress_marks:
    :param active_limit:
    :param recent_limit:
    :return: Move map {row_id: new_group} (??)

    """

    # Group rows
    groups = _group_status(status_dict)

    # Check group counts
    def active_size(_groups):
        return len(_groups.get(ACTIVE1, [])) + len(_groups.get(ACTIVE2, []))

    def active_queue_size(_groups):
        return len(_groups.get(ACTIVEQ, []))

    def recent_size(_groups):
        return len(_groups.get(RECENT1, [])) + len(_groups.get(RECENT2, []))

    def recent_queue_size(_groups):
        return len(_groups.get(RECENTQ, []))

    # move words from recent queue to recent1 until recent1+2 is full or queue is empty
    while recent_size(groups) < recent_limit:
        # Stop moving elements if the list is empty
        if len(groups.get(RECENTQ, [])) == 0:
            break
        else:
            row = groups[RECENTQ].pop(0)
            logging.debug("Moving row {}: recent queue --> recent 1".format(row))
            groups.setdefault(RECENT1, []).append(row)

    # move words from active queue to active1 until active1+2 is full or queue is empty
    while active_size(groups) < active_limit:
        # Stop moving elements if the list is empty
        if len(groups.get(ACTIVEQ, [])) == 0:
            break
        else:
            row = groups[ACTIVEQ].pop(0)
            logging.debug("Moving row {}: active queue --> active 1".format(row))
            groups.setdefault(ACTIVE1, []).append(row)

    # move words from not seen to active until active1+2 is full or not seen is empty
    while active_size(groups) < active_limit:
        # Stop moving elements if the list is empty
        if len(groups.get(NOTSEEN, [])) == 0:
            break
        else:
            row = groups[NOTSEEN].pop(0)
            logging.debug("Moving row {}: not seen --> active 1".format(row))
            groups.setdefault(ACTIVE1, []).append(row)

    learning_status_mod = _ungroup_status(groups)
    return learning_status_mod
