"""multiple choice exam

Python 3
"""

from copy import deepcopy
import random
from typing import Optional
from . import abc_settings, misc
from .question import (TBilingualQuestion, MCBilingualQuestion, MCQuestion, OpenQuestion)
from .question_db import QuestionDB

class ExamSettings(abc_settings.ABCSettings):
    EXAMPLE = """## randomization
seed: 322
shuffle_questions: 1
shuffle_answers: 1
ignore_topic: 0
"""

    @property
    def seed(self):
        return self._optional("seed", default=None)

    @property
    def shuffle_questions(self):
        return self._optional("shuffle_questions", default=False)

    @property
    def shuffle_answers(self):
        return self._optional("shuffle_answers", default=False)

    @property
    def ignore_topic(self) -> bool:
        return bool(self._optional("ignore_topic", default=False))


class Exam(QuestionDB):


    def __init__(self,
                 question_db: QuestionDB,
                 name: str = "No Exam Name",
                 collection: Optional[str]=None,
                 sort_by_topics: bool = True,
                 counter_in_title: bool = True,
                 question_label: bool = True,
                 quest_info: bool = False):
        """adds all selected questions

        if collection is defined all questions from the collection are used,
        otherwise selected ("XX") questions.
        """
        super().__init__()
        self.name = name
        self.question_label = question_label
        self.quest_info = quest_info
        cnt = 0
        # copy selected
        for q in question_db.questions:
            if collection is None:
                sel = q.selected
            else:
                sel = collection in q.collection
            if sel:
                q = deepcopy(q)
                if counter_in_title:
                    cnt += 1
                    q.title = f"{cnt}: {q.title}"
                else:
                    q.title = f"{q.title}"
                self.add_question(q, sort_by_topics=False)


        if sort_by_topics:
            self.sort_by_topics()
        # unselect_all
        self.unselect_all()

    @property
    def short_hash(self):
        rtn = ""
        for h in self.question_hash_list:
            rtn += "{}\n".format(h)
        return misc.short_hash(rtn)

    def __str__(self):
        """returns string of all questions """

        rtn = ""
        for cnt, question in enumerate(self._questions):
            rtn += "# {} --- topic {} --- {} -------------\n".format(cnt+1,
                                                                     question.topic, question.short_hash)
            if isinstance(question, TBilingualQuestion):
                rtn += "L1: {0}\nL2: {1}\n".format(question.L1.question,
                                                   question.L2.question)
            else:
                rtn += "{0}\n".format(question.question) # type: ignore
        return rtn

    def shuffle_questions(self, sort_by_topics=True):
        """randomize order of questions.

        You can keep are particular sort for instance of topics. Randomizing
        will then find place only within categories."""

        random.shuffle(self._questions)
        if sort_by_topics:
            self.sort_by_topics()

    def shuffle_answers(self):
        for x in self._questions:
            if isinstance(x, (MCBilingualQuestion, MCQuestion)):
                x.shuffle_answers()

    @property
    def test_matrix(self) -> dict:
        """returns dict with tuple of question id and points for each taxonomy level
            (changes after question order is changed)"""

        taxo = []
        points = []
        question = []
        topic = []
        for cnt, q in enumerate(self._questions):
            cnt += 1

            question.append(cnt)
            taxo.append(q.taxonomy)
            points.append(q.points)
            topic.append(q.topic)

            if isinstance(q, OpenQuestion):
                letter = 0
                for cat, pnt in zip(q.part_taxonomies, q.part_points):
                    tmp = "{}{}".format(cnt, chr(ord('a') + letter))
                    question.append(tmp)
                    taxo.append(cat)
                    points.append(pnt)
                    topic.append(q.topic)
                    letter += 1

        return {"question": question,
                             "taxonomy": taxo,
                             "topic": topic,
                             "points": points}

    @property
    def question_hash_list(self):
        return list(map(lambda q: q.short_hash, self._questions))

    def get_short_hashes_bilingual(self) -> dict:
        rtn = {"id": [], "L1": [], "L2": []}
        for cnt, quest in enumerate(self._questions):
            if isinstance(quest, TBilingualQuestion):
                rtn["id"].append(cnt+1)
                rtn["L1"].append(quest.L1.short_hash)
                rtn["L2"].append(quest.L2.short_hash)
        return rtn

    def get_solution_summary(self, line_suffix_str="",
                             as_numbers_starting_with_zero=True,
                             as_letters=True,
                             with_hash=True):
        """returns all solutions as text"""

        txt = ""
        for x, question in enumerate(self._questions):
            if isinstance(question, (MCQuestion, MCBilingualQuestion)):
                if isinstance(question, MCBilingualQuestion):
                    question = question.L1

                if with_hash:
                    txt += line_suffix_str + "Q{0}, {1}, ".format(x+1,
                                                                  question.short_hash)
                else:
                    txt += line_suffix_str + "Q{0}, ".format(x+1)

                txt += str(question.correct_answer_ids(
                    as_numbers_starting_with_zero, as_letters=as_letters))[
                    1:-1].replace("'", "")
                txt += "\n"

        if len(txt) > 0:  # include varnames
            if with_hash:
                txt = line_suffix_str + "question, hash, solution\n" + txt
            else:
                txt = line_suffix_str + "question, solution\n" + txt

        return txt


def make_exam(settings:ExamSettings, database:QuestionDB)->  Exam:

    exam = Exam(question_db=database,
                name=settings.name,
                sort_by_topics=settings.ignore_topic)
    exam.print_summary()

    if settings.seed is not None:
        random.seed(settings.seed)

    if settings.shuffle_questions:
        print(" shuffling questions")
        exam.shuffle_questions(sort_by_topics=not settings.ignore_topic)

    if settings.shuffle_answers:
        print(" shuffling answers")
        exam.shuffle_answers()
    return exam
