import unittest
import openpyxl
import pickle
from copy import deepcopy

from vocabulary import dataaccess, alternatives
from vocabulary import learningprogress
from vocabulary import vocabulary

from tests.utils import TEST_DICT_PATH, reset_test_env
from vocabulary.models import Flashcard, Question, WordList, WordCollection
from typing import Dict

import logging
logging.basicConfig(level=logging.INFO)


def write_test_data(name: str, test_object):
    with open("testdata/" + name + ".pickle", 'wb+') as f:
        pickle.dump(test_object, f)


def load_test_data(name):
    with open("testdata/" + name + ".pickle", 'rb') as f:
        test_object = pickle.load(f)
    return test_object


class TestFileMgr(unittest.TestCase):

    def setUp(self):
        reset_test_env()

    def test_load_save_workbook(self):
        testdict_in = TEST_DICT_PATH
        testdict_out = TEST_DICT_PATH

        word_collection = dataaccess.load_wordlist_book(wb_path=testdict_in)

        # Verify if the data was loaded successfully
        #  by taking a few datapoints as a sample
        word_list = deepcopy(word_collection.word_lists["shorttest"])
        assert word_list.lang1 == "Finnish"
        assert word_list.lang2 == "English"
        assert word_list.flashcards[2] == Flashcard(
            lang1="talo", lang2="house", remarks="")
        assert word_list.flashcards[16] == Flashcard(
            lang1="mutta", lang2="but", remarks="")
        assert word_list.flashcards[8] == Flashcard(
            lang1="uudet + t", lang2="new (plural)", remarks="t: plural marker, uudet naapurit")

        # Modifying some fields and saving the workbook
        word_list.flashcards[2].lang1 = "first row lang1"
        word_list.flashcards[3].lang2 = "second row lang2"
        word_list.flashcards[4].remarks = "4th row remarks"
        learning_progress_codes = word_list.learning_progress_codes
        learning_progress_codes[5] = 5
        word_list.learning_progress_codes = learning_progress_codes
        word_collection.word_lists["shorttest"] = word_list
        dataaccess.save_wordlist_book(wb_path=testdict_out, word_collection=word_collection)

        # Load workbook directly from openpyxl to verify modified fields
        wb = openpyxl.load_workbook(testdict_out)
        assert wb["shorttest"]["A2"].value == "first row lang1"
        assert wb["shorttest"]["B3"].value == "second row lang2"
        assert wb["shorttest"]["C6"].value == "uusi naapuri"
        assert wb["shorttest"]["C4"].value == "4th row remarks"
        assert wb["shorttest"]["D5"].value == 5


class TestLearningProgress(unittest.TestCase):

    def setUp(self):
        pass

    def test_learning_progress(self):
        learning_progress_base: Dict[int, str] = {key: None for key in range(1, 101)}

        def get_average_learning_progress(no_of_repetitions, learnprog_base):
            # Simulate use with only correct answers
            lp_value = {}
            for case in range(10):
                learnprog_dict = learningprogress.reset_progress(learnprog_base)

                for i in range(0, no_of_repetitions*len(learnprog_dict.keys())):
                    learnprog_dict, selected_key, show_flashcard = learningprogress.pick_word(
                        learnprog_dict, 5, 25)
                    learningprogress.submit_answer(learnprog_dict, selected_key, True)

                learning_progress_percentage = learningprogress.calculate_learning_progress(learnprog_dict)
                lp_value[case] = learning_progress_percentage

            return sum(lp_value.values())/len(lp_value.values())

        # By giving 3 correct answers for each question (in average), I need to reach at least 80% progress
        average_learning_progress = get_average_learning_progress(3, learning_progress_base)
        expected_learning_progress = 0.8
        assert average_learning_progress >= expected_learning_progress,\
            str(f"Learning progress is below the expected {expected_learning_progress} with the value of"
                f" {average_learning_progress}")

        # 1 correct answer --> max. 50% progress
        average_learning_progress2 = get_average_learning_progress(1, learning_progress_base)
        expected_learning_progress = 5
        assert average_learning_progress2 <= expected_learning_progress, \
            str(f"Learning progress is above the expected {expected_learning_progress} with the value of"
                f" {average_learning_progress2}")


class TestVocabulary(unittest.TestCase):
    def setUp(self) -> None:
        # Create a new copy of the testdict
        reset_test_env()

    def test_vocabulary(self):

        voc = vocabulary.Vocabulary()
        voc.load(TEST_DICT_PATH)
        # TODO handle the temporary lack of rights to the excel sheet (e. g. it's currently being edited)
        # TODO how will the object let the caller to know what has been chosen and what hasn't?
        #  E. g. choosing a bad file after a good one

        # Verify that an exception is raised when a non-existent sheet is tried to be opened
        with self.assertRaises(ValueError):
            voc.set_current_word_sheet("non-existent sheet name")
        voc.set_current_word_sheet("shorttest")

        # Verify the object types of choice_quiz()
        show_flashcard, question, flashcard = voc.choice_quiz()
        assert type(question) is Question
        assert type(flashcard) is Flashcard
        assert type(show_flashcard) is bool

        # Verify if the answer is marked as correct
        # choice_quiz function returns a flashcard, that contains the
        # correct answer, this will be then provided as an answer
        # so it must be deemed correct by answer_choice_quiz
        is_correct, flashcard2 = voc.answer_choice_quiz(flashcard.lang1)
        assert is_correct

        # Verify app behaviour with an incorrect answer
        show_flashcard, question, flashcard = voc.choice_quiz()
        is_correct, flashcard2 = voc.answer_choice_quiz("BAD ANSWER")
        assert not is_correct

        # Verify if learning progress is reset
        voc.reset_progress()
        assert voc.get_progress() == 0

        # Verify that the application functions in a stable
        # manner after asking and answering many questions
        for _ in range(0, 120):
            show_flashcard, question, flashcard = voc.choice_quiz()

            # TODO Implement duplications filter in the answer options
            # assert len(set(question.options)) == len(question.options)
            voc.answer_choice_quiz(flashcard.lang1)

        # Verify that after answering many questions, the learning progress
        # is between 0 and 1
        # See more detailed testing of the learning progress in TestLearningProgress
        learning_progress = voc.get_progress()
        print("Learning progress after correct answers: {}".format(learning_progress))
        assert 0 <= learning_progress <= 1

        # Verify that after saving and reloading, learning progress is retained correctly
        voc.save()
        del voc
        voc = vocabulary.Vocabulary()
        voc.load(TEST_DICT_PATH)
        voc.set_current_word_sheet("shorttest")
        learning_progress_2 = voc.get_progress()
        assert learning_progress == learning_progress_2, "Learning progress changed after reopening the workbook."


class TestAlternatives(unittest.TestCase):

    def setUp(self):
        self.pool1 = ["aaa", "aab", "aac", "aad", "aae", "abb", "acc", "add", "aee", "aab"]

    def test_duplicates(self):

        # Verify that in case there are fewer elements in the list than the given
        # shortlist_count or picked_count, the function will still succeed
        similar_options = alternatives.most_similar(expression="aaa",
                                                    pool=self.pool1,
                                                    shortlist_count=15,
                                                    picked_count= 15,
                                                    similarity_func=alternatives.calc_similarity)

        # Verify that the function doesn't return expression in the alternative
        assert "aaa" not in similar_options
        # Verify that there are no duplicates
        assert len(similar_options) == len(set(similar_options))

    def test_picked_count(self):
        # Verify that when there are more alternatives than the picked_count,
        # the application will return picked_count pieces of expressions
        similar_options = alternatives.most_similar(expression="aaa",
                                                    pool=self.pool1,
                                                    shortlist_count=5,
                                                    picked_count= 5,
                                                    similarity_func=alternatives.calc_similarity)
        assert len(similar_options) == 5

    def test_shortlist(self):
        # Verify if all the elements from the shortlist are picked eventually
        # by repeating the alternative generation many times
        shortlist_count = 3

        similar_options = set([])
        for _ in range(0, 100):
            similar_options = similar_options.union(set(alternatives.most_similar(expression="aaa",
                                                        pool=self.pool1,
                                                        shortlist_count=shortlist_count,
                                                        picked_count= 3,
                                                        similarity_func=alternatives.calc_similarity)))
        assert len(similar_options) == shortlist_count