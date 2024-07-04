from copy import deepcopy
from pathlib import Path
from typing import List, OrderedDict, Union

from ..misc import FILE_ENCODING, all_files, write_if_different
from ..question_db import QuestionDB
from ..exam import Exam
from .md_lib import MDTopic, question_to_markdown
from .load import SUFFIX


def save_database_folder(db: QuestionDB,
                         path: Union[str, Path],
                         remove_empty_files: bool = True) -> List[Path]:
    """returns list with saved files"""

    # prepare folder (optionally clear uncollection files)
    path = Path(path)
    if path.is_file():
        raise RuntimeError(
            f"can't created a folder. {path} is a existing files.")
    elif path.is_dir():
        # get all files with suffix
        old_files = [x.absolute() for x in all_files(path, suffix=SUFFIX)]
    else:
        path.mkdir(exist_ok=True)
        old_files = []

    md_dict = _database_to_md_dict(db, topic_headings=True,
                                   question_label=False, short_hash=True,
                                   quest_info=True, selected_only=False)
    saved_files: List[Path] = []
    for topic, txt in md_dict.items():
        topic = topic.lower().replace(" ", "_")
        saved_files.append(path.joinpath(topic).with_suffix(SUFFIX).absolute())
        write_if_different(file_path=saved_files[-1], content=txt)
        try:
            old_files.remove(saved_files[-1])
        except ValueError:
            pass

    # remove or clear not collection files
    for fl in old_files:
        if remove_empty_files:
            fl.unlink()
        else:
            # clear
            with open(fl, 'w', encoding=FILE_ENCODING) as f:
                f.truncate(0)

    # write ignored
    if len(db.ignored_content) > 0:
        with open(path.joinpath("markdown_content.ignored"),
                "a", encoding=FILE_ENCODING) as fl:
            fl.write(db.ignored_content)
    return saved_files


def save_database_file(db: QuestionDB, path: Union[str, Path]):
    """save the database in a single file

    wrapper of `save_markdown_file` that  ensures that all data are correctly saved
    """
    return save_markdown_file(db, path, topic_headings=False,
                              short_hash=True,  selected_only=False)

def save_markdown_file(db: QuestionDB,
                       path: Union[str, Path],
                       topic_headings: bool = False,
                       short_hash: bool = True,
                       selected_only: bool = False):
    if isinstance(db, Exam):
        content = f"# {db.name}\n\n"
    else:
        content = ""
    if isinstance(db, Exam):
        question_label = db.question_label
        quest_info = db.quest_info
    else:
        question_label = False
        quest_info = True
    md_dict = _database_to_md_dict(db, topic_headings=topic_headings,
                                   question_label=question_label,
                                   short_hash=short_hash,
                                   quest_info=quest_info,
                                   selected_only=selected_only)

    content += "\n".join(md_dict.values())

    # ẃrite
    path = Path(path)
    write_if_different(path, content)
    if len(db.ignored_content) > 0:
        with open(path.with_suffix(path.suffix+".ignored"),
                  "a", encoding=FILE_ENCODING) as fl:
            fl.write(db.ignored_content)


def _database_to_md_dict(db: QuestionDB,
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
