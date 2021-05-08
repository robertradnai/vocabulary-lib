# Purpose

- To create quiz rounds based on the word lists
  and on the alternative expression repositories, 
  taking the user's learning progress into consideration.
  - A quiz round consists of a batch of flashcards and quizzes
    in a fixed order.
  - A flashcard consists of an expression in one language, 
    its translation to another language and additional remarks.
  - A word list consists of flashcards, language information
    and the learning progress.
- To show the learning progress to the user as a percentage.
- To reset the learning progress of the word list on request.
- To update the learning progress of the user after they 
  answer the multiple-choice quizzes.
- To list all expressions (in only one language) from a collection of
  word lists, these help in generating alternative (incorrect) answers
  for the multiple-choice quizzes.
- To read flashcards from CSV files so that existing Excel
  tables can be easily used. The CSV files don't contain the 
  learning progress.
- To add the learning progress to the word list
  by reading it from a human- and machine-readable
  file. Saving the learning progress to such a file 
  shall also be possible.

# How to install
* cd into the repository root
* ```shell script
    pip install .
    ```
# How to use
```python
from vocabulary.vocabulary import Vocabulary
voc = Vocabulary()
# Load Excel word list (lang1: first column, lang2: second column, remarks: third column).
# Fourth column must be left empty
voc.load("word_list.xlsx")
# Choose a sheet
voc.set_current_word_sheet("sheet name")
# Get a question
show_flashcard, question, flashcard = voc.choice_quiz()
# Answer question
is_correct, flashcard2 = voc.answer_choice_quiz("answer")
# Get learning progress
learning_progress = voc.get_progress()
# Save learning progress
voc.save()
```
# How to create binary package and source distribution
```
pip install --upgrade setuptools wheel
python setup.py sdist bdist_wheel
```