"""Exams with Python and Latex

see cmd_line_interface for examples

Oliver Lindemann
"""

__version__ = "0.12.2"
__author__ = 'Oliver Lindemann'

from . import question
from .exam import Exam, ExamSettings, make_exam
from .question_db import QuestionDB
