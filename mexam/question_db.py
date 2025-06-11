"""
"""

from itertools import groupby
from typing import List, Optional, Union
from uuid import UUID

from .question import TQuestion


class QuestionDB(object):

    def __init__(self):
        self._questions: List[TQuestion] = []
        self.ignored_content: str = ""

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

    @property
    def n_selected(self):
        """returns number of selected questions"""
        cnt = 0
        for x in self._questions:
            if x.selected:
                cnt +=1
        return cnt

    def get_collections(self) -> List[str]:
        """returns a list of all collections"""
        collections = set()
        for x in self._questions:
            if x.collection:
                collections.update(x.collection)
        return sorted(list(collections))

    def print_summary(self) -> None:
        """prints a summary of the question database"""
        print(f"questions: {self.n_questions}")
        cnt = 0
        for key, group in groupby(
                map(lambda x: x.topic, self._questions)):
            cnt += 1
            n = len(list(group))
            print(f" topic {cnt}: n = {n}, {key}")

    def print_collections_selections(self) -> None:
        """prints a summary of the question database with collections and selections"""
        print(f"collections: {len(self.get_collections())}")
        for coll in self.get_collections():
            print(f"  {coll}: {len([x for x in self._questions if coll in x.collection])}")
        print(f"selected: {self.n_selected}")

    def unselect_all(self):
        for x in self._questions:
            x.selected = False

    def store_collection(self, tag:str):
        """store selected items using the property 'collection'"""
        for x in self._questions:
            if x.selected:
                x.collection.add(tag)
                x.selected = False

    def set_collection(self, tag:str, keep_selected:bool = False):
        """selects all items that have the 'collection' tag"""
        for x in self._questions:
            if keep_selected and x.selected:
                continue
            x.selected = tag in x.collection

    def remove_collection(self, tag:str):
        """removes the collection tag from all items"""
        for x in self._questions:
            if tag in x.collection:
                x.collection.remove(tag)

    def get_question(self, uuid:Union[str, UUID]) -> Union[None, TQuestion]:
        if isinstance(uuid, str):
            uuid = UUID(uuid)
        for x in self._questions:
            if x.uuid == uuid:
                return x