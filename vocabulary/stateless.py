"""
Vocabulary main module

"""
import logging

from . import dataaccess

import random
from . import alternatives, learningprogress
from typing import Callable, Dict
from .models import Question, Flashcard, QuizPackage
from .models import WordCollection, WordList
from .vocabulary import _choice_quiz, _check_answer, _build_word_pool, _update_learning_progress
from .vocabulary import _get_learning_progress
from .learningprogress import submit_answer, pick_words, Progress, PickOrder
from pdb import set_trace

VSTATUS_LOAD_FILE = 1
VSTATUS_CHOOSE_SHEET = 2
VSTATUS_READY_FOR_QUIZ = 3

SHOW_FLASHCARD_KEY_NAME = "showFlashcard"


def _build_quiz(word_list: WordList, row_key: int, alternatives_pool, flashcard_only: bool) -> QuizPackage:

    flashcard = Flashcard(
        lang1=word_list.flashcards[row_key].lang1,
        lang2=word_list.flashcards[row_key].lang2,
        remarks=word_list.flashcards[row_key].remarks,
    )

    if flashcard_only:
        question = None
    else:
        incorrect_alternatives = alternatives.most_similar(flashcard.lang1, alternatives_pool, 50, 4,
                                                           alternatives.calc_similarity)

        question = Question(row_key=row_key,
                            text=flashcard.lang2,
                            options=[flashcard.lang1] + incorrect_alternatives)
        random.shuffle(question.options)

    quiz_package = QuizPackage(directives={SHOW_FLASHCARD_KEY_NAME: flashcard_only},
                               question=question,
                               flashcard=flashcard)
    return quiz_package



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

        # Pick 5 expressions, get flashcards and alternatives
        learning_progress_dict: Dict[int, str] = _get_learning_progress(self._get_word_list(word_list_name))
        row_keys_new = pick_words(learning_progress_dict=learning_progress_dict,
                                  filter_by_progress=lambda p: p == Progress.NEW,
                                  order=PickOrder.ORIGINAL,
                                  max_count_from_size=lambda v:  5)

        row_keys_recent = pick_words(learning_progress_dict=learning_progress_dict,
                                     filter_by_progress=lambda p: p == Progress.RECENT,
                                     order=PickOrder.SHUFFLED,
                                     max_count_from_size=lambda v:  5)

        row_keys_learned = pick_words(learning_progress_dict=learning_progress_dict,
                                      filter_by_progress=lambda p: p == Progress.LEARNED,
                                      order=PickOrder.SHUFFLED,
                                      max_count_from_size=lambda size:  3 if size > 10 else 0)

        flashcards_only = [_build_quiz(word_list=self._get_word_list(word_list_name),
                           row_key=row_key,
                        alternatives_pool=None,
                         flashcard_only=True) for row_key in row_keys_new]
        new_questions = [_build_quiz(word_list=self._get_word_list(word_list_name),
                           row_key=row_key,
                           alternatives_pool=self.word_pool_lang1,
                           flashcard_only=False) for row_key in row_keys_new]
        random.shuffle(new_questions)

        recent_questions = [_build_quiz(word_list=self._get_word_list(word_list_name),
                                     row_key=row_key,
                                     alternatives_pool=self.word_pool_lang1,
                                     flashcard_only=False) for row_key in row_keys_recent]
        random.shuffle(recent_questions)

        learned_questions = [_build_quiz(word_list=self._get_word_list(word_list_name),
                                        row_key=row_key,
                                        alternatives_pool=self.word_pool_lang1,
                                        flashcard_only=False) for row_key in row_keys_learned]
        random.shuffle(learned_questions)

        quiz_packages = flashcards_only + new_questions + recent_questions + learned_questions

        return quiz_packages

    def update_progress(self, word_list_name: str, row_key, q_correctly_answered: bool):
        """
        Check the given answer if it's correct or not correct. Update the learning progress based on the answer.
        :return:
        """

        word_list = self._get_word_list(word_list_name)
        learning_progress_mod = submit_answer(_get_learning_progress(word_list),
                                              row_key, q_correctly_answered)
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



