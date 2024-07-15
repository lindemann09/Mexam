from copy import deepcopy
from typing import OrderedDict

from .. import question as q
from ..exam import Exam
from ..question_db import QuestionDB
from .md_lib import MDQuestionHeader, MDTopic


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


def database_to_md_dict(db: QuestionDB,
                         topic_headings: bool,
                         question_label: bool,
                         short_hash: bool,
                         quest_info: bool,
                         selected_only: bool) -> OrderedDict:
    """separate mds pre topic
    """
    curr = None
    topic_mds = OrderedDict()
    for q in db.questions:
        if selected_only and not q.selected:
            continue
        if curr != q.topic:
            # new topic
            curr = q.topic
            topic_mds[curr] = ""
            if topic_headings:
                topic_mds[curr] += MDTopic(curr).markdown()

        if topic_headings:
            q = deepcopy(q)
            q.topic = ""

        topic_mds[curr] += question_to_markdown(q, question_label=question_label,
                                                short_hash=short_hash,
                                                quest_info=quest_info) + "\n\n"

    return topic_mds


def database_to_markdown(db: QuestionDB,
                       topic_headings: bool = False,
                       short_hash: bool = True,
                       selected_only: bool = False) -> str:
    if isinstance(db, Exam):
        content = f"# {db.name}\n\n"
        question_label = db.question_label
        quest_info = db.quest_info
        selected_only = False
    else:
        content = ""
        question_label = False
        quest_info = True

    md_dict = database_to_md_dict(db, topic_headings=topic_headings,
                                   question_label=question_label,
                                   short_hash=short_hash,
                                   quest_info=quest_info,
                                   selected_only=selected_only)

    content += "\n".join(md_dict.values())

    return content