from os import makedirs, path
from typing import Dict, List

from ..exam import Exam
from ..question import MCBilingualQuestion, MCQuestion
from ..misc import FILE_ENCODING, MultiCounter, bool_str, underline

FILE_SUFFIX = ".Rmd"

class _RExamMCItem(object):

    def __init__(self, exname:str, mc_question:MCQuestion):
        # escape slashes to ensure correct rendering of latex commands

        self.exname = exname
        self.question = mc_question.question
        self.exshuffle = len(mc_question.fixed_position_answers()) == 0
        self.exsection = f"P{mc_question.title}"
        self.exextra_taxonomy = mc_question.taxonomy

        self.answer_list = []
        self.exsolution = ""
        for a in mc_question.answers:
            self.answer_list.append(a.text)
            if a.is_correct:
                self.exsolution += "1"
            else:
                self.exsolution += "0"

    def __str__(self):
        return self.content(escape_slashes=False)

    @property
    def answerlist_str(self):
        rtn = ""
        for x in self.answer_list:
            rtn += "* {}\n".format(x)
        return rtn

    def content(self, escape_slashes):
        if escape_slashes:
            question = self.question.replace("\\", "\\\\")
            answerlst_str =self.answerlist_str.replace("\\", "\\\\")
        else:
            question = self.question
            answerlst_str =self.answerlist_str

        rtn = underline("Question", "=") + "\n"
        rtn += question.rstrip() + "\n\n"
        rtn += underline("Answerlist", "-") + "\n"
        rtn += answerlst_str.rstrip() + "\n\n"
        rtn += underline("Meta-information", "=") + "\n"
        rtn += "exname: {}\nextype: schoice\nexsolution: {}\n".format(
                            self.exname, self.exsolution)
        rtn += "exshuffle: {}\n".format(bool_str(self.exshuffle))
        if self.exsection is not None:
            rtn += "exsection: {}\n".format(self.exsection)
        if self.exextra_taxonomy is not None:
            rtn += "exextra[Taxonomy]: {}\n".format(self.exextra_taxonomy)
        return rtn

    def save(self, escape_slashes, directory=None, add_subfolder=False):
        if directory is None:
            directory = ""
        directory = path.abspath(directory)

        if add_subfolder:
            directory = path.join(directory, self.exname)

        if not path.isdir(directory):
            makedirs(directory)

        with open(path.join(directory, self.exname + FILE_SUFFIX),
                  "w", encoding=FILE_ENCODING) as fl:
            fl.write(self.content(escape_slashes=escape_slashes))


def convert(exam:Exam,
            name:str,
            incl_hash:bool=False,
            directory:str="rexam",
            escape_slashes:bool=True,
            add_subfolder:bool=True) -> Dict[str, List]:

    print("Export to RExams, destination folder: {}".format(directory))
    cnt = MultiCounter()

    files = {}
    for biquest in exam.questions:
        assert isinstance(biquest, MCBilingualQuestion) # TODO works currently only for MCBilingual questions
        qtype = "P{}".format(biquest.title)
        cnt.inc(qtype)
        for quest in [biquest.L1, biquest.L2]:
            qname = "{}-{}-{}-{}".format(name, qtype,
                                         str(cnt.get(qtype)).zfill(2),
                                         quest.language)
            if incl_hash:
                qname += "-{}".format(quest.short_hash)

            rmd = _RExamMCItem(exname=qname, mc_question=quest)
            rmd.save(escape_slashes=escape_slashes, directory=directory, add_subfolder=add_subfolder)

            if quest.language not in files:
                files[quest.language] = []
            files[quest.language].append(rmd.exname + FILE_SUFFIX)

    return files

