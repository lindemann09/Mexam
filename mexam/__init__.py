"""Managing multilingual exam questions in markdown

MEXAM command line tool for managing multilingual exam questions in markdown format.
It allows you to create, edit, and organize exam questions in multiple languages.

Oliver Lindemann
"""

__version__ = "0.16-dev0"
__author__ = 'Oliver Lindemann'

from . import question
from .exam import Exam, ExamSettings, make_exam
from .question_db import QuestionDB
