import unittest

from tests.utils import reset_test_env, TEST_DICT_PATH, TEST_DICT_PARQUET_PATH
from vocabulary.models import Question, Flashcard, QuizPackage
from vocabulary.stateless import Vocabulary
from vocabulary.dataaccess import load_wordlist_book, \
    word_collection_to_pickle, word_collection_from_pickle
from typing import List


class TestVocabulary(unittest.TestCase):
    def setUp(self) -> None:
        # Create a new copy of the testdict
        reset_test_env()

    def test_vocabulary(self):

        # Creating the Vocabulary object from an Excel workbook
        voc = Vocabulary()
        voc.load(TEST_DICT_PATH, load_wordlist_book)
        word_list_name = "shorttest"
        quiz_strategy = "adaptive"
        voc.reset_progress(word_list_name)

        # TODO handle the temporary lack of rights to the excel sheet (e. g. it's currently being edited)
        # TODO how will the object let the caller to know what has been chosen and what hasn't?
        #  E. g. choosing a bad file after a good one

        # Verify if the necessary objects are returned
        quiz_list: List[QuizPackage] = voc.choice_quiz(word_list_name, quiz_strategy)
        assert type(quiz_list[5].question) is Question  # The first few entries are flashcards only
        assert type(quiz_list[0].flashcard) is Flashcard
        assert type(quiz_list[0].directives['showFlashcard']) is bool

        # Verify if the answer is marked as correct
        # choice_quiz function returns a flashcard, that contains the
        # correct answer, this will be then provided as an answer
        # so it must be deemed correct by answer_choice_quiz

        answers_without_keys = [True, True, False, True, False]

        for i in range(5, len(quiz_list)): # The first 5 entries are flashcards
            voc.update_progress(word_list_name, quiz_list[i].question.row_key, answers_without_keys[i-5])

        # Verify if the correctly answered questions had an effect on the learning progress
        learning_progress = voc.get_progress(word_list_name)
        assert (0 < learning_progress < 1)

        # Verify if learning progress can reach 1 (but doesn't exeed it) after enough answers
        # Verify that the application functions in a stable
        # manner after asking and answering many questions
        for _ in range(0, 120):
            quiz_list2: List[QuizPackage] = voc.choice_quiz(word_list_name, quiz_strategy)
            for i in range(0, len(quiz_list2)): # The first 5 entries are flashcards
                if not quiz_list2[i].directives["showFlashcard"]:
                    voc.update_progress(word_list_name, quiz_list2[i].question.row_key, True)

        # Verify that after answering many questions, the learning progress
        # reaches 1
        # See more detailed testing of the learning progress in TestLearningProgress
        learning_progress2 = voc.get_progress(word_list_name)
        assert learning_progress2 == 1

        voc.save(TEST_DICT_PARQUET_PATH, word_collection_to_pickle)

        # Verify that learning progress is properly saved by saving and loading the word collection
        voc2 = Vocabulary()
        voc2.load(TEST_DICT_PARQUET_PATH, word_collection_from_pickle)
        assert learning_progress2 == voc2.get_progress(word_list_name)
