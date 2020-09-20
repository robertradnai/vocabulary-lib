"""
Algorithms for generating similar but incorrect alternatives to the correct answer.
"""

from ngram import NGram
from random import shuffle
from typing import List, Callable


def most_similar(expression: str, pool: List[str], shortlist_count: int,
                 picked_count: int, similarity_func: Callable[[str, List[str]], List[int]]) -> List[str]:
    """
    Find how_many other words that are similar to the correct answer so that the choice quiz will be harder
    :param expression:
    :param pool:
    :param shortlist_count:
    :param picked_count:
    :param similarity_func: function to calculate the similarity of expressions
    :return: List of the most similar expressions
    """
    # Removing duplicates
    pool_without_duplicates = list(set(pool) - set([expression]))
    similarity = similarity_func(expression, pool_without_duplicates)
    similar_options = _pick_highest_ranking(pool_without_duplicates, similarity, shortlist_count,
                                            picked_count, exclude_list=[])
    return similar_options


def calc_similarity(expression_str: str, alternative_list: List[str]) -> List[int]:
    """
    Calculate the similarity between expression_str and the strings in alternative_list
    :param expression_str:
    :param alternative_list:
    :return:
    """
    expr = str(expression_str)  # Sometimes the type is unicode
    similarity = []  # key: alternative expression, val: similarity index

    for altexpr in alternative_list:
        # Creating a similarity indicator based on the following:
        #   n-gram comparison
        #   word count
        #   character count
        indicator = {'ngram': NGram.compare(str(expr), altexpr),
                     'wordcount': 1 - abs(len(altexpr.split()) - len(expr.split())) / (
                             len(expr.split()) + len(altexpr.split())),
                     'charcount': 1 - abs(len(altexpr) - len(expr)) / (
                             len(expr) + len(altexpr)), 'specchars': 0}

        if (not expr.find("?") == -1) and not (altexpr.find("?") == -1):
            indicator['specchars'] += 1
        if (not expr.find("!") == -1) and not (altexpr.find("!") == -1):
            indicator['specchars'] += 1

        similarity.append(sum(indicator.values()))
    return similarity


def _pick_highest_ranking(expr_list, ranking, pool_count, picked_count, exclude_list=None):
    if exclude_list is None:
        exclude_list = []
    zipped_list = list(zip(expr_list, ranking))
    # Sort by ranking value
    zipped_list.sort(key=lambda v: v[1], reverse=True)

    # Build a pool of the <pool_count> most similar words
    # Exclude expressions from the exclude_list
    pool = []
    for val in zipped_list:
        if not val[0] in exclude_list:
            pool.append(val[0])
        if len(pool) >= pool_count:
            break

    shuffle(pool)

    # Pick <pick_count words from pool>
    picked_list = pool[:picked_count]
    return picked_list
