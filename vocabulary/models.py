from typing import Dict, List


class Question:
    def __init__(self, row_key, text: str, options: list):
        self.row_key = row_key
        self.text = text
        self.options = options


class Flashcard:
    def __init__(self, lang1: str, lang2: str, remarks: str, learning_status: int):
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
    def __init__(self, progress):
        self.progress = progress


class WordList:
    def __init__(self, name, lang1: str, lang2:str, flashcards: Dict[int, Flashcard]):
        self.name = name
        self.lang1 = lang1
        self.lang2 = lang2
        self.flashcards = flashcards


class WordCollection:
    def __init__(self, lang1: str, lang2: str, word_lists: Dict[str, WordList]):
        self.lang1 = lang1
        self.lang2 = lang2
        self.word_lists = word_lists
