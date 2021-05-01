from typing import Dict, List


class Question:
    def __init__(self, row_key, text: str, options: list):
        self.row_key = row_key
        self.text = text
        self.options = options


class Flashcard:
    def __init__(self, lang1: str, lang2: str, remarks: str, learning_status: int = 0):
        self.lang1 = lang1
        self.lang2 = lang2
        self.remarks = remarks
        self.learning_status = learning_status

    def __eq__(self, other):
        if not isinstance(other, Flashcard):
            return NotImplemented
        return self.lang1 == other.lang1 and self.lang2 == other.lang2 and self.remarks == other.remarks and \
               self.learning_status == other.learning_status


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
    def __init__(self, name, lang1: str, lang2: str, flashcards: Dict[int, Flashcard],
                 learning_progress_codes: Dict[int, int] = None):

        self.__name = name
        self.__lang1: str = lang1
        self.__lang2: str = lang2
        self.__flashcards: Dict[int, Flashcard] = flashcards

        if learning_progress_codes is None:
            self.learning_progress_codes = {}
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
        if len(learning_progress_codes) != len(self.__flashcards):
            raise ValueError(f"Size of flashcards ({len(self.__flashcards)})"
                             f"doesn't equal to size of learning progress codes"
                             f" ({len(learning_progress_codes)})")
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
