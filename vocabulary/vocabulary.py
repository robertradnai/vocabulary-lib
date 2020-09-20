"""
Vocabulary main module

"""
import logging

from . import dataaccess

import random
from . import alternatives, learningprogress
from .models import Question, Flashcard
from typing import Dict
from .models import WordCollection, WordList

VSTATUS_LOAD_FILE = 1
VSTATUS_CHOOSE_SHEET = 2
VSTATUS_READY_FOR_QUIZ = 3


def _choice_quiz(word_list: WordList, word_pool: list) -> (bool, dict, dict):
    active_limit = 5
    recent_limit = 50

    learning_progress_dict: Dict[int, str] = _get_learning_progress(word_list)

    new_progress_dict, row_key = \
        learningprogress.pick_word(learning_progress_dict, active_limit, recent_limit)
    new_word_list = _update_learning_progress(word_list, new_progress_dict)

    flashcard = Flashcard(
        lang1=word_list.flashcards[row_key].lang1,
        lang2=word_list.flashcards[row_key].lang2,
        remarks=word_list.flashcards[row_key].remarks,
        learning_status=word_list.flashcards[row_key].learning_status
    )

    incorrect_alternatives = alternatives.most_similar(flashcard.lang1, word_pool, 50, 4,
                                                       alternatives.calc_similarity)

    question = Question(row_key=row_key,
                        text=flashcard.lang2,
                        options=[flashcard.lang1] + incorrect_alternatives)
    random.shuffle(question.options)

    # If the word is seen for the first time, a flashcard will be shown instead of the question
    show_flashcard = (flashcard.learning_status == 1)
    return new_word_list, show_flashcard, question, flashcard


def _check_answer(question: Question, answer: str, word_list: WordList) -> (bool, dict):
    """
    Check in the actual wordlist_dict object whether the given answer is correct
    Then modify learning status and return the modified word_dict
    :param question:
    :param answer:
    :param word_list:
    :return:
    """
    flashcard = word_list.flashcards[question.row_key]

    # Is the answer correct?
    if flashcard.lang1 == answer:
        is_correct = True
    else:
        is_correct = False

    # Modify word_dict accordingly
    learning_progress_mod = learningprogress.submit_answer(_get_learning_progress(word_list),
                                                           question.row_key, is_correct)

    word_list_mod = _update_learning_progress(word_list, learning_progress_mod)

    return is_correct, flashcard, word_list_mod


def _build_word_pool(word_collection: WordCollection) -> (list, list):
    """
    Create a list of words from the current words in the whole Excel workbook
    (it’s assumed that all the sheets contain entries from a single language)
    :param word_collection:
    :return:
    """

    word_pool_lang1 = []
    word_pool_lang2 = []

    for sheet_name in word_collection.word_lists:
        for flashcard in word_collection.word_lists[sheet_name].flashcards.values():
            word_pool_lang1.append(flashcard.lang1)
            word_pool_lang2.append(flashcard.lang2)

    return word_pool_lang1, word_pool_lang2


def _update_learning_progress(word_list: WordList, learning_progress_dict: Dict[int, str]):

    new_flashcards = {row: Flashcard(lang1=flashcard.lang1,
                                     lang2=flashcard.lang2,
                                     remarks=flashcard.remarks,
                                     learning_status=learning_progress_dict[row])
                      for row, flashcard in word_list.flashcards.items()}

    word_list.flashcards = new_flashcards
    return word_list


def _get_learning_progress(word_list: WordList) -> Dict[int, str]:
    return {key: flashcard.learning_status for key, flashcard
            in word_list.flashcards.items()}


class Vocabulary:
    """
    Provide the Vocabulary library functionalities: e. g. loading word list, picking and answering questions,
    getting and resetting learning progress.

    """

    def __init__(self):
        self.status = VSTATUS_LOAD_FILE
        self.wb_path: str = None
        self.workbook = None
        self.word_collection: WordCollection = None
        self._current_question = None
        self.word_pool_lang1 = None
        self.word_pool_lang2 = None
        self.selected_word_list_name = None

    def load(self, wb_path: str):

        self.word_collection, self.workbook = dataaccess.load_wordlist_book(wb_path)
        self.word_pool_lang1, self.word_pool_lang2 = _build_word_pool(self.word_collection)
        self.wb_path = wb_path
        self.status = VSTATUS_CHOOSE_SHEET

    def save(self):
        dataaccess.save_wordlist_book(self.wb_path, self.word_collection)

    def get_word_sheet_list(self) -> list:
        return list(self.word_collection.word_lists.keys())  # It only returns valid worksheets

    def get_current_word_sheet(self):
        if not self.status == VSTATUS_READY_FOR_QUIZ:
            raise Exception("No sheet was chosen for the quiz.")
        return self.selected_word_list_name

    def set_current_word_sheet(self, word_sheet_name: str):
        if word_sheet_name in self.workbook.sheetnames:
            self.selected_word_list_name = word_sheet_name
        else:
            raise ValueError("Invalid sheet name")
        self.status = VSTATUS_READY_FOR_QUIZ

    def choice_quiz(self) -> (bool, Question, Flashcard):
        """
        Fetch a question from the given word sheet. Generate one correct and several incorrect answer options.
        Return the text of the question (e. g. pick the correct answer) and the answer options for the question.

        :return: whether to show the flashcard (instead of the question), Question, Flashcard
        """
        if type(self._current_question) is Question:
            logging.warning("choice_quiz was called again without answering the question from the previous call")

        new_word_list, show_flashcard, question, flashcard = _choice_quiz(self.get_current_word_list(),
                                                           self.word_pool_lang1)
        self.set_current_word_list(new_word_list)

        self._current_question = question

        return show_flashcard, question, flashcard

    def get_current_word_list(self) -> WordList:
        return self.word_collection.word_lists[self.get_current_word_sheet()]

    def set_current_word_list(self, word_list: WordList):
        self.word_collection.word_lists[self.get_current_word_sheet()] = word_list

    def answer_choice_quiz(self, answer: str):
        """
        Check the given answer if it's correct or not correct. Update the learning progress based on the answer.
        :param answer: The answer that will be checked.
        :return:
        """
        if type(self._current_question) is not Question:
            raise Exception("No question was asked")
        is_correct, flashcard, word_list = _check_answer(
            self._current_question, answer, self.get_current_word_list()
        )
        self.set_current_word_list(word_list)
        self._current_question = None
        return is_correct, flashcard

    # Calculates the learning progress
    def get_progress(self):
        return learningprogress.calculate_learning_progress(
            _get_learning_progress(self.get_current_word_list()))

    def reset_progress(self):
        word_list = self.get_current_word_list()
        learning_progress_dict = learningprogress.reset_progress(
            _get_learning_progress(word_list)
        )
        self.set_current_word_list(_update_learning_progress(word_list, learning_progress_dict))
