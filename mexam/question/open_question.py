
from typing import Any, Dict, Optional, Union
from uuid import UUID

from .base import TOneLangQuestion


class OpenQuestion(TOneLangQuestion):  # question with parts

    def __init__(self, question: str,
                 selected:bool,
                 title: str | None = None,
                 topic: Union[int, str, None] = None,
                 taxonomy: Union[int, str, None] = None,
                 language: str = "?",
                 points: Optional[float] = None,
                 uuid: Optional[UUID | str] = None,
                 collection: Optional[str] = None,
                 info: Optional[Dict[str, Any]] = None):
        super().__init__(question=question,
                         selected=selected,
                         topic=topic,
                         title=title,
                         taxonomy=taxonomy,
                         language=language,
                         points=points,
                         uuid=uuid,
                         collection=collection,
                         additional_info=info)
        self._parts = []
        self.part_points = []
        self.part_taxonomies = []

    def to_text(self) -> str:
        rtn = super().to_text()
        if len(self._parts)>0:
            rtn+= "\n"
            for txt in self._parts:
                rtn += " * " + txt + "\n"
        return rtn

    @property
    def n_parts(self):
        return len(self._parts)

    @property
    def parts(self):
        return self._parts

    def add_part(self, question: str, points: float = 0, taxonomy: Union[int, str, None] = None):
        self._parts.append(question)
        self.part_points.append(int(points))
        self.part_taxonomies.append(taxonomy)

