import copy
import random
from typing import List, Dict, Optional

from vocabulary import WordList, alternatives
from vocabulary.learningprogress import pick_words, PickOrder, Progress, submit_answer, calculate_learning_progress, \
    reset_progress
from vocabulary.models import MultipleChoiceQuiz, Flashcard, QuizEntry, RenderedFlashcard


def create_quiz_round(word_list: WordList, quiz_type: str, alternative_answers: List[str]):

    """
    Fetch a question from the given word sheet. Generate one correct and several incorrect answer options.
    Return the text of the question (e. g. pick the correct answer) and the answer options for the question.

    :return: whether to show the flashcard (instead of the question), Question, Flashcard
    """

    # Pick 5 expressions, get flashcards and alternatives

    row_keys_new = pick_words(learning_progress_dict=word_list.learning_progress_codes,
                              filter_by_progress=lambda p: p == Progress.NEW,
                              order=PickOrder.ORIGINAL,
                              max_count_from_size=lambda v:  5)

    row_keys_recent = pick_words(learning_progress_dict=word_list.learning_progress_codes,
                                 filter_by_progress=lambda p: p == Progress.RECENT,
                                 order=PickOrder.SHUFFLED,
                                 max_count_from_size=lambda v:  5)

    row_keys_learned = pick_words(learning_progress_dict=word_list.learning_progress_codes,
                                  filter_by_progress=lambda p: p == Progress.LEARNED,
                                  order=PickOrder.SHUFFLED,
                                  max_count_from_size=lambda size:  3 if size > 10 else 0)

    flashcards_only = [__build_quiz_entry(word_list=word_list,
                                          row_key=row_key,
                                          alternatives_pool=None,
                                          flashcard_only=True) for row_key in row_keys_new]
    new_questions = [__build_quiz_entry(word_list=word_list,
                                        row_key=row_key,
                                        alternatives_pool=alternative_answers,
                                        flashcard_only=False) for row_key in row_keys_new]
    random.shuffle(new_questions)

    recent_questions = [__build_quiz_entry(word_list=word_list,
                                           row_key=row_key,
                                           alternatives_pool=alternative_answers,
                                           flashcard_only=False) for row_key in row_keys_recent]
    random.shuffle(recent_questions)

    learned_questions = [__build_quiz_entry(word_list=word_list,
                                            row_key=row_key,
                                            alternatives_pool=alternative_answers,
                                            flashcard_only=False) for row_key in row_keys_learned]
    random.shuffle(learned_questions)

    quiz_entries = flashcards_only + new_questions + recent_questions + learned_questions

    return quiz_entries


def get_learning_progress(word_list: WordList) -> float:
    return calculate_learning_progress(word_list.learning_progress_codes)


def reset_learning_progress(word_list) -> WordList:

    word_list.learning_progress_codes = reset_progress(
        word_list.learning_progress_codes)
    return word_list


def submit_answers(word_list, answers: Dict[int, bool]):

    for row_key, is_correct in answers.items():
        word_list.learning_progress_codes = submit_answer(
            word_list.learning_progress_codes, row_key, is_correct)

    return copy.deepcopy(word_list)


def __build_quiz_entry(word_list: WordList, row_key: int, alternatives_pool,
                       flashcard_only: bool) -> QuizEntry:

    if flashcard_only:
        question: Optional[MultipleChoiceQuiz] = None
        flashcard: Optional[RenderedFlashcard] = RenderedFlashcard(
            lang1=word_list.flashcards[row_key].lang1,
            lang2=word_list.flashcards[row_key].lang2,
            remarks=word_list.flashcards[row_key].remarks,
            lang1_header=word_list.lang1,
            lang2_header=word_list.lang2,
            remarks_header="Remarks"
        )

    else:
        flashcard: Optional[RenderedFlashcard] = None

        incorrect_alternatives = alternatives.most_similar(word_list.flashcards[row_key].lang1,
                                                           alternatives_pool, 50, 4,
                                                           alternatives.calc_similarity)

        options = [word_list.flashcards[row_key].lang1] + incorrect_alternatives
        random.shuffle(options)

        correct_answer_indices = [options.index(word_list.flashcards[row_key].lang1)]

        question: Optional[MultipleChoiceQuiz] = MultipleChoiceQuiz(
            row_key=row_key,
            instruction_header=word_list.lang2,
            instruction_content=word_list.flashcards[row_key].lang2,
            options_header=f"{word_list.lang1} - How would you translate?",
            options=options,
            correct_answer_indices=correct_answer_indices)

    return QuizEntry(question=question, flashcard=flashcard)



