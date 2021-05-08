# TODO write new tests
import json
import unittest
import logging
import random
from collections import Counter
from dataclasses import dataclass
from functools import reduce
from typing import List, Dict
import copy

from vocabulary import WordList
from vocabulary.dataaccess import read_flashcards_from_csv_string, build_word_list, \
    save_word_list_learning_progress_json
from vocabulary.models import QuizEntry
from vocabulary.wordlistquiz import create_quiz_round, submit_answers, get_learning_progress

logging.basicConfig(level=logging.INFO)


def get_flashcards_csv_str():
    with open("testdata/testdict_shorttest.csv") as f:
        flashcards_csv_str = f.read()
    return flashcards_csv_str


def get_quiz_row_keys(quiz_round):
    return [entry.question.row_key for entry in quiz_round if entry.question is not None]


def next_answer_cycle(word_list: WordList, alternatives_list: List[str], good_answer_chance: float):
    quiz_round = create_quiz_round(word_list, "", alternatives_list)

    assert 0 <= good_answer_chance <= 1

    def generate_answer():
        rnd = random.random()
        return True if rnd > 1-good_answer_chance else False

    answers = {key: generate_answer() for key in get_quiz_row_keys(quiz_round)}

    word_list_updated = submit_answers(word_list, answers)

    learning_progress = get_learning_progress(word_list_updated)
    return word_list_updated, QuizProgressTest(quiz_round, answers, learning_progress)


@dataclass
class QuizProgressTest:
    quiz_round: List[QuizEntry]
    answers: Dict[int, int]
    learning_progress_after: int


def run_test_rounds(repetitions: int) -> List[QuizProgressTest]:
    with open("testdata/alternatives_finnish_vocabulary1.csv") as f:
        alternatives_str = f.read()
    alternatives_str.replace("\r", "")
    alternatives_list = alternatives_str.split("\n")

    with open("testdata/testdict_shorttest.csv") as f:
        flashcards_csv_str = f.read()
    word_list = build_word_list("Finnish", "English", flashcards_csv_str)

    progress_tests = []
    for _ in range(0, repetitions):
        word_list, progress_test = next_answer_cycle(word_list, alternatives_list, 1)
        progress_tests.append(progress_test)

    for _ in range(0, repetitions):
        word_list, progress_test = next_answer_cycle(word_list, alternatives_list, 0)
        progress_tests.append(progress_test)

    return progress_tests


class TestWordListDao(unittest.TestCase):

    def test_build_word_list_without_learning_progress(self):

        word_list = build_word_list("Finnish", "English", get_flashcards_csv_str())

        assert word_list.lang1 == "Finnish"
        assert word_list.lang2 == "English"
        assert 16 == len(word_list.flashcards)
        assert 16 == len(word_list.learning_progress_codes)

    def test_build_word_list_with_learning_progress(self):

        learning_progress = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 0, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1,
                             11: 1, 12: 1, 13: 1, 14: 1, 15: 1}

        word_list = build_word_list("Finnish", "English", get_flashcards_csv_str(),
                                    save_word_list_learning_progress_json(learning_progress))

        assert 1 == word_list.learning_progress_codes[0]
        assert 3 == word_list.learning_progress_codes[2]


class TestWordListQuiz(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.quiz_rounds_results: List[QuizProgressTest] = run_test_rounds(20)

        learning_progress_values = [round_result.learning_progress_after for
                                    round_result in cls.quiz_rounds_results]

        cls.max_learning_progress = max(learning_progress_values)

        max_progress_first_index = learning_progress_values.index(cls.max_learning_progress)

        row_key_lists = [get_quiz_row_keys(round_result.quiz_round)
                         for round_result in cls.quiz_rounds_results[0:max_progress_first_index+1]]

        all_asked_row_keys = sum(row_key_lists, [])

        cls.counter = Counter(all_asked_row_keys)

        flashcard_lang1_lists = [
            [entry.flashcard.lang1 for entry in round_result.quiz_round if entry.flashcard is not None]
            for round_result in cls.quiz_rounds_results[0:max_progress_first_index+1]]

        cls.flashcard_counters = Counter(sum(flashcard_lang1_lists, []))


        cls.entry_counts = [len([entry for entry in round_result.quiz_round])
                        for round_result in cls.quiz_rounds_results[0:max_progress_first_index+1]]

        cls.quiz_counts = [len([entry for entry in round_result.quiz_round if entry.question is not None])
                       for round_result in cls.quiz_rounds_results[0:max_progress_first_index+1]]

        cls.flashcard_counts = [len([entry for entry in round_result.quiz_round if entry.flashcard is not None])
                            for round_result in cls.quiz_rounds_results[0:max_progress_first_index+1]]

    def test_quiz_round_flashcard_count(self):
        assert max(self.flashcard_counts) == 5, f"There are more than 5 flashcards" \
                                                f"fin a quiz round: {max(self.flashcard_counts)}"

    def test_quiz_round_entry_count(self):
        assert max(self.entry_counts) == 15, f"There are more than 15 entries" \
                                             f"in a quiz round: {max(self.entry_counts)}"

    def test_learning_progress_reached(self):
        assert self.max_learning_progress == 1, "Learning progress didn't reach 1 at all " \
                                                f"during the test rounds: max. value was {self.max_learning_progress}"

    def test_flashcard_frequency(self):
        for count in self.flashcard_counters.values():
            assert count == 1, f"A flashcard was shown not exactly once: {count}"

    def test_quiz_frequency(self):
        for count in self.counter.values():
            assert 2 <= count <= 4, f"A quiz was shown too many times: {count}"