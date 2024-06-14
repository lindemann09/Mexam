"""multiple choice exam"""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from .. import misc
from .base import TOneLangQuestion
from .answer import Answer


class MCQuestion(TOneLangQuestion):

    def __init__(self, question: str,
                 selected: bool,
                 title: str | None = None,
                 topic: Union[int, str, None] = None,
                 taxonomy: Union[int, str, None] = None,
                 language: str = "?",
                 points: Optional[float] = None,
                 uuid: Optional[UUID | str] = None,
                 collection: Optional[str] = None,
                 additional_info: Optional[Dict[str, Any]] = None):
        super().__init__(question=question,
                         selected=selected,
                         topic=topic,
                         taxonomy=taxonomy,
                         language=language,
                         points=points,
                         title=title,
                         uuid=uuid,
                         collection=collection,
                         additional_info=additional_info)
        self._answers = []

    def to_text(self) -> str:
        rtn = super().to_text()
        if len(self.answers) > 0:
            rtn += "\n"
            for a in self._answers:
                rtn += a.to_text()
        return rtn

    @property
    def answers(self) -> List[Answer]:
        return self._answers

    @answers.setter
    def answers(self, val: List[Answer]) -> None:
        self._answers = val

    def add_answer(self, answer, is_correct, fixed_position):
        self._answers.append(Answer(text=answer, is_correct=is_correct,
                                    fixed_position=fixed_position))

    def fixed_position_answers(self):
        return list(filter(lambda x: x.fixed_position, self._answers))

    def shuffle_answers(self):
        # answer fix positions
        return misc.shuffle_fixed_positions(self._answers,
                                            self.fixed_position_answers)

    def is_correct(self) -> List[bool]:
        return [ans.is_correct for ans in self._answers]

    def correct_str(self) -> str:
        arr = [str(int(ans.is_correct)) for ans in self._answers]
        return "".join(arr)

    def correct_answer_ids(self, as_numbers_starting_with_zero=True,
                           as_letters=False):
        """returns list of all correct answers"""
        rtn = []
        for cnt, correct in enumerate(self.is_correct()):
            if correct:
                if as_letters:
                    rtn.append(chr(ord("A")+cnt))
                elif as_numbers_starting_with_zero:
                    rtn.append(cnt)
                else:
                    rtn.append(cnt + 1)
        return rtn

    def to_old_markdown(self,
                        question_counter: Optional[int],
                        question_id: Optional[str]) -> str:
        # slightly different format as __str__
        if question_id is not None:
            rtn = f'# {question_id}'
        elif question_counter is not None:
            rtn = f'# Question {question_counter}'
        else:
            rtn = '# Question'

        rtn += f"\n\n{self.question}\n\n"
        for cnt, a in enumerate(self._answers):
            letter = chr(ord("A") + cnt)
            if a.is_correct:
                rtn += f"*{letter}*)"
            else:
                rtn += f"  {letter})"
            rtn += f" {a.text}\n\n"

        return rtn
