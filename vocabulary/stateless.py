"""
Vocabulary main module

"""
import logging

from . import dataaccess

import random
from . import alternatives, learningprogress
from .models import Question, Flashcard
from typing import Callable
from .models import WordCollection, WordList
from .vocabulary import _choice_quiz, _check_answer, _build_word_pool, _update_learning_progress
from .vocabulary import _get_learning_progress
from .learningprogress import submit_answer

VSTATUS_LOAD_FILE = 1
VSTATUS_CHOOSE_SHEET = 2
VSTATUS_READY_FOR_QUIZ = 3


class Vocabulary:
    """
    Provide the Vocabulary library functionalities: e. g. loading word list, picking and answering questions,
    getting and resetting learning progress.

    """

    def __init__(self):
        self.status = VSTATUS_LOAD_FILE
        self.word_collection: WordCollection = None
        self.word_pool_lang1 = None
        self.word_pool_lang2 = None
        self.selected_word_list_name = None

    def load(self, path: str, load_function: Callable[[str], WordCollection]):

        self.word_collection= load_function(path)
        self.word_pool_lang1, self.word_pool_lang2 = _build_word_pool(self.word_collection)

    def save(self, path: str, save_function: Callable[[str, WordCollection], None]):
        save_function(path, self.word_collection)

    def get_word_sheet_list(self) -> list:
        return list(self.word_collection.word_lists.keys())  # It only returns valid worksheets

    def choice_quiz(self, word_list_name: str, quiz_strategy: str) -> (bool, Question, Flashcard):
        """
        Fetch a question from the given word sheet. Generate one correct and several incorrect answer options.
        Return the text of the question (e. g. pick the correct answer) and the answer options for the question.

        :return: whether to show the flashcard (instead of the question), Question, Flashcard
        """

        (new_word_list,
         show_flashcard,
         question,
         flashcard) = _choice_quiz(self._get_word_list(word_list_name),
                                   self.word_pool_lang1)
        self._set_word_list(word_list_name, new_word_list)

        return show_flashcard, question, flashcard

    def update_progress(self, word_list_name: str, question: Question, q_correctly_answered: bool):
        """
        Check the given answer if it's correct or not correct. Update the learning progress based on the answer.
        :return:
        """

        word_list = self._get_word_list(word_list_name)
        learning_progress_mod = submit_answer(_get_learning_progress(word_list),
                                              question.row_key, q_correctly_answered)
        word_list_mod = _update_learning_progress(word_list, learning_progress_mod)

        self._set_word_list(word_list_name, word_list_mod)

    # Calculates the learning progress
    def get_progress(self, word_list_name):
        return learningprogress.calculate_learning_progress(
            _get_learning_progress(self._get_word_list(word_list_name)))

    def reset_progress(self, word_list_name: str):
        word_list = self._get_word_list(word_list_name)
        learning_progress_dict = learningprogress.reset_progress(
            _get_learning_progress(word_list)
        )
        self._set_word_list(word_list_name, _update_learning_progress(word_list, learning_progress_dict))

    def _get_word_list(self, word_list_name: str) -> WordList:
        return self.word_collection.word_lists[word_list_name]

    def _set_word_list(self, word_list_name: str, word_list: WordList):
        self.word_collection.word_lists[word_list_name] = word_list
