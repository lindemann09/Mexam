from abc import ABCMeta, abstractmethod
from typing import Optional, Union
from uuid import UUID

from .. import misc
from .base import TQuestion, TOneLangQuestion
from .mc_question import MCQuestion
from .open_question import OpenQuestion


class TBilingualQuestion(TQuestion, metaclass=ABCMeta):

    def __init__(self,
                 L1_question: TOneLangQuestion,
                 L2_question: TOneLangQuestion,
                 uuid: Optional[UUID | str]):

        if L1_question.language == L2_question.language:
            raise ValueError(
                "Two languages of a bilingual question are identical")
        l1_info = L1_question.get_info_dict(add_title=True, add_selected=False,
                                            add_uuid=False, add_collection=False)
        l2_info = L2_question.get_info_dict(add_title=True, add_selected=False,
                                            add_uuid=False, add_collection=False)
        if l1_info != l2_info:
            raise RuntimeError("Bilingual questions have different info dicts!\n" +
                               f"L1: {l1_info}\nL1: {l2_info}")

        super().__init__(title=L1_question.title,
                         topic=L1_question.topic,
                         taxonomy=L1_question.taxonomy,
                         points=L1_question.points,
                         selected=L1_question.selected,
                         uuid=uuid,
                         collection=L1_question.collection_string,
                         additional_info=L1_question.additional_info)

    @property
    @abstractmethod
    def L1(self) -> TOneLangQuestion:
        pass

    @property
    @abstractmethod
    def L2(self) -> TOneLangQuestion:
        pass

    def to_text(self) -> str:
        return self.L1.to_text() + "\n" + self.L2.to_text()


class MCBilingualQuestion(TBilingualQuestion):

    def __init__(self, L1_question: MCQuestion, L2_question: MCQuestion,
                 uuid: Optional[UUID | str] = None):
        assert isinstance(L1_question, MCQuestion)
        assert isinstance(L2_question, MCQuestion)
        super().__init__(L1_question, L2_question, uuid=uuid)
        self._l1 = L1_question
        self._l2 = L2_question

    @property
    def L1(self) -> MCQuestion:
        return self._l1

    @property
    def L2(self) -> MCQuestion:
        return self._l2

    def shuffle_answers(self):
        """shuffels answers of L1 and L2 in the same way"""
        joined = list(zip(self.L1.answers, self.L2.answers))
        fixed = list(filter(lambda x: x[0].fixed_position, joined))
        joined = misc.shuffle_fixed_positions(joined, fixed)
        self.L1._answers, self.L2._answers = list(zip(*joined))  # unzip

    def add_answer(self, L1_text: str, L2_text: str, is_correct: bool,
                   fixed_position: bool = False):
        self.L1.add_answer(L1_text, is_correct, fixed_position=fixed_position)
        self.L2.add_answer(L2_text, is_correct, fixed_position=fixed_position)


class BilingualOpenQuestion(TBilingualQuestion):

    def __init__(self, L1_question: OpenQuestion, L2_question: OpenQuestion,
                 uuid: Optional[UUID | str] = None):
        assert isinstance(L1_question, OpenQuestion)
        assert isinstance(L2_question, OpenQuestion)
        super().__init__(L1_question, L2_question, uuid=uuid)
        self._l1 = L1_question
        self._l2 = L2_question

    @property
    def L1(self) -> OpenQuestion:
        return self._l1

    @property
    def L2(self) -> OpenQuestion:
        return self._l2

    def add_part(self, L1_part: str, L2_part: str, points: float = 0, taxonomy: Union[int, str, None] = None):
        self.L1.add_part(L1_part, points=points, taxonomy=taxonomy)
        self.L2.add_part(L2_part, points=points, taxonomy=taxonomy)
