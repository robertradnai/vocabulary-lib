import unittest

from tests.utils import reset_test_env, TEST_DICT_PATH, TEST_DICT_PARQUET_PATH
from vocabulary.models import Question, Flashcard
from vocabulary.stateless import Vocabulary
from vocabulary.dataaccess import load_wordlist_book, \
    word_collection_to_pickle, word_collection_from_pickle


class TestVocabulary(unittest.TestCase):
    def setUp(self) -> None:
        # Create a new copy of the testdict
        reset_test_env()

    def test_vocabulary(self):

        voc = Vocabulary()
        voc.load(TEST_DICT_PATH, load_wordlist_book)
        # TODO handle the temporary lack of rights to the excel sheet (e. g. it's currently being edited)
        # TODO how will the object let the caller to know what has been chosen and what hasn't?
        #  E. g. choosing a bad file after a good one

        word_list_name = "shorttest"
        quiz_strategy = "adaptive"
        # Verify the object types of choice_quiz()
        show_flashcard, question, flashcard = voc.choice_quiz(word_list_name, quiz_strategy)
        assert type(question) is Question
        assert type(flashcard) is Flashcard
        assert type(show_flashcard) is bool

        # Verify if the answer is marked as correct
        # choice_quiz function returns a flashcard, that contains the
        # correct answer, this will be then provided as an answer
        # so it must be deemed correct by answer_choice_quiz
        is_correct = voc.update_progress(word_list_name, question, True)
        # TODO add assert

        # Verify app behaviour with an incorrect answer
        show_flashcard, question, flashcard = voc.choice_quiz(word_list_name, quiz_strategy)
        voc.update_progress(word_list_name, question, False)
        # TODO add assert

        # Verify if learning progress is reset
        voc.reset_progress(word_list_name)
        assert voc.get_progress(word_list_name) == 0

        # Verify that the application functions in a stable
        # manner after asking and answering many questions
        for _ in range(0, 120):
            show_flashcard, question, flashcard = voc.choice_quiz(word_list_name, quiz_strategy)

            # TODO Implement duplications filter in the answer options
            # assert len(set(question.options)) == len(question.options)
            voc.update_progress(word_list_name, question, True)

        # Verify that after answering many questions, the learning progress
        # is between 0 and 1
        # See more detailed testing of the learning progress in TestLearningProgress
        learning_progress = voc.get_progress(word_list_name)
        print("Learning progress after correct answers: {}".format(learning_progress))
        assert 0 <= learning_progress <= 1

        voc.save(TEST_DICT_PARQUET_PATH, word_collection_to_pickle)

        # Verify that learning progress is properly saved by saving and loading the word collection
        voc2 = Vocabulary()
        voc2.load(TEST_DICT_PARQUET_PATH, word_collection_from_pickle)
        assert learning_progress == voc2.get_progress(word_list_name)