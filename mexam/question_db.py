"""
"""

from itertools import groupby
from typing import List, Optional, Union
from uuid import UUID

from .question import TQuestion


class QuestionDB(object):

    def __init__(self):
        self._questions: List[TQuestion] = []

    @property
    def questions(self) -> List[TQuestion]:
        return self._questions

    def add_question(self, question: Optional[TQuestion],
                     sort_by_topics: bool = True) -> None:
        if question is None:
            return
        if not isinstance(question, TQuestion):
            raise RuntimeError("Please add an MCQuestion, OpenQuestion, or"
                               "their bilingual versions")
        self._questions.append(question)
        if sort_by_topics:
            self.sort_by_topics()

    def sort_by_topics(self) -> None:
        """questions by sorted by topic"""
        self._questions = sorted(self._questions,
                                 key=lambda q: (q.topic is None, str(q.topic)))
        # "Tuple trick" above:
        # Nones in list can't be sort, but tuples (True, None) can. None will be at the end, because False<True

    @property
    def n_questions(self):
        return len(self._questions)

    def print_summary(self):
        print("no_questions: {}".format(len(self._questions)))
        cnt = 0
        for key, group in groupby(
                map(lambda x: x.topic, self._questions)):
            cnt += 1
            n = len(list(group))
            print(f" topic {cnt}: n = {n}, {key}")

    def unselect_all(self):
        for x in self._questions:
            x.selected = False

    def store_collection(self, tag:str):
        """store selected items using the property 'collection'"""
        for x in self._questions:
            if x.selected:
                x.collection.add(tag)
                x.selected = False

    def set_collection(self, tag:str):
        """selects all items that have the 'collection' tag"""
        for x in self._questions:
            x.selected = tag in x.collection

    def get_question(self, uuid:Union[str, UUID]) -> Union[None, TQuestion]:
        if isinstance(uuid, str):
            uuid = UUID(uuid)
        for x in self._questions:
            if x.uuid == uuid:
                return x