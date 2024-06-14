from pathlib import Path
from typing import List, Optional, Union

from .. import question as q
from ..exam import ExamSettings
from ..misc import FILE_ENCODING, all_files
from ..question_db import QuestionDB
from .md_lib import MDQuestion, MDQuestionHeader, MDTopic
from .settings import MarkdownSettings

SUFFIX = ".md"


def load_database(path_or_setings: Union[str, Path, ExamSettings],
                  suffix: Optional[str] = None) -> QuestionDB:
    if suffix is None:
        suffix = SUFFIX

    if isinstance(path_or_setings, ExamSettings):
        ms = MarkdownSettings(parent=path_or_setings)
        if ms.md_database is None:
            path = Path("")
        else:
            path = Path(ms.md_database)
    else:
        path = Path(path_or_setings)

    if path.is_dir():
        files = all_files(path, suffix)
    elif path.is_file():
        files = [path]
    else:
        files = []

    if len(files) == 0:
        raise RuntimeError(f"Can't open file(s) in {path} (suffix={suffix})")

    lines = []
    for fl in files:
        with open(fl, "r", encoding=FILE_ENCODING) as f:
            lines.extend(f.readlines())

    return parse(lines)


class _MDParser(object):

    def __init__(self) -> None:
        self._topic = ""
        self._quest_header = None
        # question in different languages
        self._quest_langs: List[MDQuestion] = []

    def _set_quest_header(self, x: Optional[MDQuestionHeader]):
        self._quest_header = x
        self._quest_langs: List[MDQuestion] = []

    @property
    def question_in_cache(self) -> bool:
        """returns true is well defined question"""
        return isinstance(self._quest_header, MDQuestionHeader) and \
            len(self._quest_langs) > 0

    def _make_question(self) -> Union[None, q.TQuestion]:
        if self.question_in_cache:
            langs = [x.to_mexam_question(question_header=self._quest_header,  # type: ignore
                                       alt_topic=self._topic) for x in self._quest_langs]
            if len(langs) == 1:
                return langs[0]

            elif len(langs) > 1:
                if isinstance(langs[0], q.MCQuestion) and isinstance(langs[1], q.MCQuestion):
                    return q.MCBilingualQuestion(langs[0], langs[1], uuid=langs[1].uuid)
                elif isinstance(langs[0], q.OpenQuestion) and isinstance(langs[1], q.OpenQuestion):
                    return q.BilingualOpenQuestion(langs[0], langs[1], uuid=langs[1].uuid)

    def parse(self, lines: Union[str, List[str]]) -> QuestionDB:
        rtn = QuestionDB()

        if isinstance(lines, str):
            lines = lines.splitlines()

        for ln in lines:
            ln = ln.rstrip()
            x = MDTopic.create(ln)
            if x is not None:
                # new topic
                if self.question_in_cache:
                    rtn.add_question(self._make_question())
                self._set_quest_header(None)
                self._topic = x.topic
                continue

            x = MDQuestionHeader.create(ln)
            if isinstance(x, MDQuestionHeader):
                # new question
                if self.question_in_cache:
                    rtn.add_question(self._make_question())
                self._set_quest_header(x)
                continue

            if isinstance(self._quest_header, MDQuestionHeader):
                if self._quest_header.parse_info(ln):
                    continue

                x = MDQuestion.create(ln)
                if isinstance(x, MDQuestion):
                    # new question lang
                    self._quest_langs.append(x)
                    continue

                if len(self._quest_langs) > 0:
                    self._quest_langs[-1].parse(ln)

        if self.question_in_cache:
            rtn.add_question(self._make_question())

        return rtn


def parse(lines: Union[str, List[str]]) -> QuestionDB:
    return _MDParser().parse(lines)
