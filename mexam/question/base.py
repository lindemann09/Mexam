"""base classes"""
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from typing import Any, Dict, Optional,  Union
from uuid import UUID, uuid4
from .. import misc

NO_TOPIC = ""


class TQuestion(metaclass=ABCMeta):

    def __init__(self,
                 title: Optional[str],
                 topic: Union[int, str, None],
                 taxonomy: Union[int, str, None],
                 points: Optional[float],
                 selected: bool,
                 uuid: Optional[UUID | str],
                 collection: Optional[str],
                 additional_info: Optional[Dict[str, Any]]):

        if title is None:
            self.title = ""
        else:
            self.title = title
        if topic is None:
            self.topic = ""
        else:
            self.topic = str(topic)
        if taxonomy is None:
            self.taxonomy = ""
        else:
            self.taxonomy = str(taxonomy)
        if points is None:
            self.points = 1
        else:
            self.points = points
        self.selected = selected

        if collection is None:
            self.collection = set()
        else:
            self.collection = set([x.strip() for x in collection.split(",")])
            self.collection.discard("")

        if uuid is None:
            self.uuid = uuid4()
        elif isinstance(uuid, UUID):
            self.uuid = uuid
        else:
            self.uuid = UUID(uuid)

        self._additional_info = {}
        if additional_info is not None:
            self.additional_info = additional_info

    @property
    def short_uuid(self) ->str:
        return str(self.uuid)[:6]

    @property
    def additional_info(self) -> Dict[str, Any]:
        return self._additional_info

    @additional_info.setter
    def additional_info(self, val:Dict[str, Any]):
        bad = [k for k in ("title", "taxonomy", "topic",
                           "points", "selected", "uuid", "collection") if k in val]
        if len(bad)>0:
            raise ValueError("The following keys are not allowed as additional info:\n" +
                             f"{bad}. Use object properties.")

        self._additional_info = val

    @property
    def collection_string(self) -> str:
        return ", ".join(sorted(self.collection))

    def get_info_dict(self, add_title:bool,
                      add_selected:bool,
                      add_uuid:bool,
                      add_collection:bool) -> Dict[str, Any]:

        if add_title:
            d:Dict[str, Any] = {"title": self.title}
        else:
            d:Dict[str, Any] = {}
        d.update({"taxonomy": self.taxonomy,
             "topic": self.topic,
             "points": self.points})

        if add_selected:
            d.update({"selected": self.selected})
        if add_uuid:
            d.update({"uuid": str(self.uuid)})
        if add_collection:
            d.update({"collection": self.collection_string})
        d.update(self.additional_info)
        return d

    @property
    def short_hash(self):
        return misc.short_hash(self.to_text())

    @property
    def __str__(self):
        return self.to_text()

    @abstractmethod
    def to_text(self) -> str:
        pass


class TOneLangQuestion(TQuestion):

    def __init__(self,
                 question: str = "",
                 language: str = "",
                 selected: bool = False,
                 title: Optional[str]  = None,
                 topic: Union[int, str, None] = None,
                 taxonomy: Union[int, str, None] = None,
                 points: Optional[float] = None,
                 uuid: Optional[UUID | str] = None,
                 collection: Optional[str] = None,
                 additional_info: Optional[Dict[str, Any]] = None):

        super().__init__(title=title, topic=topic, taxonomy=taxonomy,
                         points=points, selected=selected, uuid=uuid,
                         collection=collection,
                         additional_info=additional_info)

        self.question = misc.strip_lines(question)
        self.language = language

    def label(self, short_hash:bool=True, title:bool=True) -> str:
        """language and uuid and optionally short hash and title"""

        rtn = f"{self.language}_{self.short_uuid}"
        if short_hash:
            rtn = f"{rtn}_{self.short_hash}"
        if title:
            t = self.title
            for x in ".'!,&|;\"()": # remove chars
                t = t.replace(x, "")
            t = t.strip().replace(" ", "_")
            rtn = f"{rtn}_{t}"

        return rtn

    def to_dict(self) -> OrderedDict:
        rtn = OrderedDict({"Question": self.question, "hash": self.short_hash})
        rtn.update(self.get_info_dict(add_title=True, add_selected=True,
                                      add_uuid=True, add_collection=True))
        return rtn

    def to_text(self) -> str:
        return self.question + "\n"
