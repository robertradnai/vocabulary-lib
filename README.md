# Purpose

- This library creates quiz rounds based on the word lists
  and on the alternative expression repositories
- A quiz round consists of flashcards and multiple-choice quizzes
  in a fixed order, these will be shown to the user
- The library generates alternative expression repositories from 
  word lists, these help in generating alternative (incorrect) answers
  for the multiple-choice quizzes

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