"""database markdown definitions"""

from copy import deepcopy
import re
from typing import List, Optional, Union

from typing_extensions import Self

from .. import question as q
from ..misc import number_to_string

class MDTopic(object):
    NO_TOPIC = "Undefined"
    HEAD = re.compile(r"^\s*#\s+(.*)")  # # (...)

    def __init__(self, topic: str):
        self.topic = topic

    def __str__(self):
        return self.markdown()

    def markdown(self) -> str:
        if len(self.topic) == 0:
            topic = MDTopic.NO_TOPIC
        else:
            topic = self.topic

        return f"# {topic}\n\n"

    @classmethod
    def create(cls, txt: str) -> Optional[Self]:
        m = cls.HEAD.match(txt)
        if m is not None:
            return cls(topic=m.groups()[0].strip())


class MDQuestionHeader(object):

    SELECT_TAG = "XX"
    HEAD = re.compile(r"^\s*##\s+(.*)")  # (...)
    INFO = re.compile(r"^\s*\[(.+)\]:\s*(.+)?")  # "[(...)]: (....)"

    cnt = 0

    def __init__(self,
                 title: str,
                 selected: bool,
                 info: Optional[dict] = None):

        if len(title) == 0:
            MDQuestionHeader.cnt += 1
            self.title = f"Question {MDQuestionHeader.cnt}"
        else:
            self.title = title
        self.selected = selected
        if info is None:
            self.info = {}
        else:
            self.info = info

    def __str__(self):
        return self.markdown()

    def markdown(self) -> str:
        """ title prefix is presented as part of the title, before the question title.
        This function can be collection for question counter"""

        rtn = "## " + self.title
        if self.selected:
            rtn += f" {self.SELECT_TAG}"
        rtn += "\n"
        if len(self.info) > 0:
            rtn += "\n"
            # information
            for k, v in self.info.items():
                if v is not None and v != "":
                    if isinstance(v, (int, float)):
                        #try to convert to string without decimals
                        v = number_to_string(v)
                    rtn += f"[{k}]: {v}\n"

        return rtn + "\n"

    @classmethod
    def create(cls, txt: str) -> Optional[Self]:
        m = cls.HEAD.match(txt)
        if m is not None:
            txt = m.groups()[0].strip()
            x = txt.split(" ")
            selected = x[-1].strip() == cls.SELECT_TAG
            if selected:
                x.pop()  # delete SELECT_TAG
            return cls(title=" ".join(x).strip(),
                       selected=selected,
                       info={})

    def parse_info(self, txt):
        m = self.INFO.match(txt)
        if m is not None:
            key, value = m.groups()
            if value is None:
                value = ""
            self.info[key] = value
            return True
        return False


class MDQuestion(object):
    # TODO FIXED POSITION NOT IMPLEMENTED

    ANSWER = re.compile(r"^\s*-\s+(\*X\*)?\s*(.*)")  # "- (*X*) (...)"
    # **NL 56232**, or **EN**
    QUEST_LANG = re.compile(r"^\s*\*\*(\w+)\s*(\w*)\*\*\s*$")

    def __init__(self,
                 language: str,
                 short_hash: str,
                 text: str = "",
                 answers: Optional[List[q.Answer]] = None):

        self.text = text
        self.language = language
        self.short_hash = short_hash
        if answers is None:
            answers = []
        self.answers: List[q.Answer] = answers

    @classmethod
    def create(cls, txt: str) -> Optional[Self]:
        m = cls.QUEST_LANG.match(txt)
        if m is not None:
            a, b = m.groups()
            return cls(language=a, short_hash=b)

    def parse(self, txt: str):
        m = self.ANSWER.match(txt)
        if m is not None:
            correct_tag, txt = m.groups()
            # add answer option
            self.answers.append(q.Answer(text=txt,
                                         is_correct=isinstance(correct_tag, str)))
        elif len(self.answers) > 0:
            # append to last answer
            add_txt = txt.strip()
            if len(add_txt) > 0:
                self.answers[-1].text += " " + add_txt
        else:
            # add to text
            self.text += f"{txt}\n"

    def to_mexam_question(self,
                      question_header: MDQuestionHeader,
                      alt_topic="") -> Union[q.OpenQuestion,  q.MCQuestion]:
        """returns a Mexam Open or MC Question"""

        qh = deepcopy(question_header)
        try:
            topic = qh.info.pop("topic")
        except KeyError:
            topic = alt_topic
        try:
            taxonomy = qh.info.pop("taxonomy")
        except KeyError:
            taxonomy = None
        try:
            points = float(qh.info.pop("points"))
        except (KeyError, ValueError):
            points = None
        try:
            uuid = qh.info.pop("uuid")
        except KeyError:
            uuid = None
        try:
            collection = qh.info.pop("collection")
        except KeyError:
            collection = None


        if len(self.answers) > 0:
            # MC Question
            rtn = q.MCQuestion(title=qh.title,
                               question=self.text.strip(),
                               topic=topic,
                               language=self.language,
                               taxonomy=taxonomy,
                               points=points,
                               uuid=uuid,
                               collection=collection,
                               selected=qh.selected,
                               additional_info=qh.info)
            rtn.answers = self.answers
        else:
            # OpenQuestion
            rtn = q.OpenQuestion(title=qh.title,
                                 question=self.text.strip(),
                                 topic=topic,
                                 language=self.language,
                                 taxonomy=taxonomy,
                                 points=points,
                                 selected=qh.selected,
                                 uuid=uuid,
                                 collection=collection,
                                 info=qh.info)

        if self.short_hash != rtn.short_hash:
            print(f"  not fitting hash: {self.short_hash} -> {rtn.short_hash}")

        return rtn


def _to_markdown(quest: q.TOneLangQuestion, question_label: bool, short_hash: bool) -> str:
    if question_label:
        rtn = quest.label(short_hash=short_hash)
    else:
        rtn = f"{quest.language}"
        if short_hash:
            rtn += f" {quest.short_hash}"

    if len(rtn) > 0:
        rtn = f"**{rtn.strip()}**\n\n"
    rtn += quest.to_text()
    return rtn


def question_to_markdown(quest: q.TQuestion,
                     question_label: bool = False,
                     short_hash: bool = True,
                     quest_info: bool = True) -> str:
    """Convert question to markdown"""
    if quest_info:
        info = quest.get_info_dict(add_title=False, add_selected=False,
                                   add_uuid=True, add_collection=True)
    else:
        info = {}
    rtn = MDQuestionHeader(title=quest.title,
                           selected=quest.selected,
                           info=info).markdown()
    if isinstance(quest, q.TBilingualQuestion):
        return rtn + _to_markdown(quest.L1, question_label=question_label, short_hash=short_hash) + \
            "\n" + _to_markdown(quest.L2, question_label=question_label, short_hash=short_hash)

    else:
        return rtn + _to_markdown(quest, question_label=question_label, short_hash=short_hash) # type: ignore
