from dataclasses import dataclass
from typing import Dict, List
from dataclasses_json import dataclass_json, LetterCase


class Question:
    def __init__(self, row_key, text: str, options: list):
        self.row_key = row_key
        self.text = text
        self.options = options


class Flashcard:
    def __init__(self, lang1: str, lang2: str, remarks: str):
        self.lang1 = lang1
        self.lang2 = lang2
        self.remarks = remarks

    def __eq__(self, other):
        if not isinstance(other, Flashcard):
            return NotImplemented
        return self.lang1 == other.lang1 and self.lang2 == other.lang2 and self.remarks == other.remarks


class LearningProgress:
    def __init__(self):
        self.flashcards: Dict[int, int] = {}

    def set_flashcard_progress(self, flashcard_key: int, learning_progress_code: int):
        self.flashcards[flashcard_key] = learning_progress_code

    def set_all_flashcards_progress(self, learning_progress_code):
        self.flashcards = {k: learning_progress_code for k, v in self.flashcards.items()}


class LearningProgressEntry:
    def __init__(self, learning_progress_code: int):
        self.learning_progress_code = learning_progress_code


class WordList:
    def __init__(self, lang1: str, lang2: str, flashcards: Dict[int, Flashcard],
                 learning_progress_codes: Dict[int, int] = None, name=None):

        self.__name = name
        self.__lang1: str = lang1
        self.__lang2: str = lang2
        self.__flashcards: Dict[int, Flashcard] = flashcards

        if learning_progress_codes is None:
            self.learning_progress_codes = {k: 1 for k in self.__flashcards.keys()}
        else:
            self.learning_progress_codes = learning_progress_codes

    @property
    def name(self) -> str:
        return self.__name

    @property
    def lang1(self) -> str:
        return self.__lang1

    @property
    def lang2(self) -> str:
        return self.__lang2

    @property
    def flashcards(self) -> Dict[int, Flashcard]:
        return self.__flashcards

    @property
    def learning_progress_codes(self) -> Dict[int, int]:
        return {k: v.learning_progress_code for k, v in self.__learning_progress.items()}

    @learning_progress_codes.setter
    def learning_progress_codes(self, learning_progress_codes: Dict[int, int]):
        learning_progress_keys = set(learning_progress_codes.keys())
        flashcard_keys = set(self.__flashcards.keys())

        if learning_progress_keys != flashcard_keys:
            raise ValueError("Flashcards and learning_progress_codes don't have the same keys!")
        else:
            self.__learning_progress = {k: LearningProgressEntry(v) for k, v in learning_progress_codes.items()}


class WordCollection:
    def __init__(self, lang1: str, lang2: str, word_lists: Dict[str, WordList]):
        self.lang1: str = lang1
        self.lang2: str = lang2
        self.word_lists: Dict[str, WordList] = word_lists


class QuizPackage:
    def __init__(self, directives: dict, question: Question, flashcard: Flashcard):
        self.directives = directives
        self.question = question
        self.flashcard = flashcard


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Flashcard:
    lang1: str
    lang2: str
    remarks: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RenderedFlashcard(Flashcard):
    lang1_header: str
    lang2_header: str
    remarks_header: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MultipleChoiceQuiz:
    row_key: int
    instruction_header: str
    instruction_content: str
    options_header: str
    options: List[str]
    correct_answer_indices: List[int]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class QuizEntry:
    question: MultipleChoiceQuiz
    flashcard: Flashcard
