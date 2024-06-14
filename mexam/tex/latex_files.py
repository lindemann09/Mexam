"""Text function and Latex Code"""
import os
from typing import Optional

from .. import __version__, misc
from ..exam import Exam
from ..question import TBilingualQuestion, MCQuestion, OpenQuestion
from .latex import text2latex
from .settings import LatexSettings

_END_QUESTION = """
    \\end{minipage}
	\\vspace{6ex}
    %\\newpage % each questions one page
}
"""

MC_QUEST_CHOICES = """
\\newenvironment{mcquestchoices}[1]{
    \\begin{minipage}{\\linewidth}
	\\question{\\bf #1}
	\\vspace{3ex}
    \\begin{choices}
	}{
	\\end{choices}""" + _END_QUESTION

MC_QUEST_CHECKBOXES = MC_QUEST_CHOICES.replace("choices", "checkboxes")

OPEN_QUESTION = """
\\newenvironment{openquestion}[3]{
    \\begin{minipage}{\\linewidth}
	\\question[#2]{\\bf #1} #3
    }{""" + _END_QUESTION

OPEN_QUESTION_WITH_PARTS = """
\\newenvironment{openquestionwithparts}[3]{
    \\begin{minipage}{\\linewidth}
	\\question[#2]{\\bf #1} #3
	\\vspace{3ex}
	\\begin{parts}
	}{
	\\end{parts}""" + _END_QUESTION

ALL = MC_QUEST_CHOICES + MC_QUEST_CHECKBOXES + OPEN_QUESTION_WITH_PARTS + \
    OPEN_QUESTION


class LatexFiles(object):

    def __init__(self,
                 tex_settings: LatexSettings):

        assert isinstance(tex_settings, LatexSettings)
        self._ts = tex_settings

    def tex_files_exist(self, language=None):
        """is_tex_file_defined() with out parameter returns if both languages are
        initialized.

        If language parameter is define it return on the initialization status
        of one language.

        """

        if language is None:
            return self.tex_files_exist(1) and \
                (not self._ts.is_multi_language or self.tex_files_exist(2))
        elif language == 1:
            return os.path.isfile(self._ts.tex_file[0])
        elif language == 2:
            return os.path.isfile(self._ts.tex_file[1])
        else:
            return False

    def create_tex_files(self):

        if not self.tex_files_exist(language=1):
            print("  Creating new tex document: {}".format(
                self._ts.tex_file[0]))
            with open(self._ts.tex_file[0], "w", encoding=misc.FILE_ENCODING) as fl:
                fl.write(self._tex_main_file(language=1))

        if self._ts.is_multi_language and not self.tex_files_exist(language=2):
            print("  Creating new tex document for second language: {}".format(
                self._ts.tex_file[1]))
            with open(self._ts.tex_file[1], "w", encoding=misc.FILE_ENCODING) as fl:
                fl.write(self._tex_main_file(language=2))

    def create_question_files(self, exam: Exam):

        # returns dict with filenames and content hashes
        quest_file = self._ts.quest_file
        # quest files
        txt = self._exam_to_latex(exam=exam, language=1,
                                   max_questions_per_page=None,
                                   add_solutions_in_comments=True)

        rtn = {quest_file[0]: misc.long_hash(txt)}
        with open(quest_file[0], 'w', encoding=misc.FILE_ENCODING) as fl:
            fl.write(txt)

        if len(quest_file[1]) > 0:
            txt = self._exam_to_latex(exam=exam, language=2,
                                       max_questions_per_page=None,
                                       add_solutions_in_comments=True)
            rtn[quest_file[1]] = misc.long_hash(txt)
            with open(quest_file[1], 'w', encoding=misc.FILE_ENCODING) as fl:
                fl.write(txt)

        return rtn

    def _tex_main_file(self, language: int) -> str:

        return """% --- Created with Mexam """ + str(__version__) + """
% --- Requires 'exam.cls' ---
\\documentclass[11pt]{exam} % add [answers] to get answers
\\usepackage[a4paper, textheight=660pt]{geometry}
\\usepackage{amssymb}
\\usepackage[none]{hyphenat}
\\usepackage{calc}
\\usepackage{color}
\\usepackage{hanging}


\\newcommand{\\examtype}{""" + self._ts.exam_title[language-1] + """}
\\newcommand{\\thedate}{""" + self._ts.date + """}
\\newcommand{\\coursetitle}{""" + self._ts.course_title + """}
\\newcommand{\\coursecode}{""" + self._ts.course_code + """}

\\pagestyle{headandfoot}
\\lhead{\\oddeven{\\coursetitle }{\\examtype{}, \\thedate}}
\\chead{}
\\rhead{\\oddeven{\\examtype{}, \\thedate }{\\sl \\coursecode}}
\\lfoot{\\oddeven{}{\\sl \\thepage{}/\\numpages}}
\\cfoot{}
\\rfoot{\\oddeven{\\sl \\thepage{}/\\numpages}{}}
\\headrule

% layout
\\checkboxchar{$\\Box$}
\\checkedchar{$\\blacksquare$}
\\CorrectChoiceEmphasis{\\color{red}\\bfseries}
\\renewcommand{\\choicelabel}{\\thechoice{})}
\\pointsdroppedatright

% question environments
""" + ALL + """

\\begin{document}
\\setcounter{page}{""" + str(self._ts.page_counter) + """}


% -------- QUESTIONS -----------
\\input{""" + self._ts.quest_file[language-1] + """}
% ------------------------------

\\end{document}
"""

    def _exam_to_latex(self, exam: Exam,
                        language: Optional[int] = None,
                        max_questions_per_page: Optional[int] = None,
                        add_solutions_in_comments: bool = True) -> str:
        """returns latex code for this xls_to_tex
        """

        rtn = "\n\n\\begin{questions}\n"
        for x, question in enumerate(exam.questions):
            if isinstance(question, TBilingualQuestion):
                if language == 1:
                    question = question.L1
                elif language == 2:
                    question = question.L2
                else:
                    raise RuntimeError("For bilingual questions, please "
                                       "specify language " +
                                       "(1 or 2) to be used!")

            rtn += "\n%Q{0} {1}\n".format(x+1, question.short_hash)
            if isinstance(question, MCQuestion):
                rtn += self.__mc_question_to_latex(question,
                                                   between_answers="")
            elif isinstance(question, OpenQuestion):
                rtn += self.__open_question_to_latex(question)
            else:
                raise RuntimeError(
                    f"Unknown question type for latex. {type(question)}")

            rtn += "\n\\vfill\n"

            if max_questions_per_page is not None and \
                    max_questions_per_page > 0 and x % 3 == 2:
                rtn += "\n \\newpage\n"

        rtn += "\n\\end{questions}\n\n"

        # add solutions
        if add_solutions_in_comments:
            return rtn + exam.get_solution_summary(line_suffix_str="% ",
                                                   as_letters=True)
        else:
            return rtn

    def __mc_question_to_latex(self,
                               quest: MCQuestion,
                               between_answers: str = "") -> str:
        """returns the latex code of for this question"""
        if self._ts.use_letters:
            answer_format = "mcquestchoices"
        else:
            answer_format = "mcquestcheckboxes"

        code = "\\begin{{{0}}}".format(answer_format) + "{\n"
        if self._ts.print_hashes:
            tmp = "[" + quest.short_hash + "] " + quest.question
        else:
            tmp = quest.question
        code += text2latex(tmp, replace_carriage_returns=True) + "}\n"
        for cnt, ans in enumerate(quest.answers):
            if ans.is_correct:
                code += "    \\CorrectChoice "
            else:
                code += "    \\choice" + ' '*8
            code += "{0}\n".format(text2latex(ans.text,
                                              replace_carriage_returns=True))
            if cnt < len(quest.answers)-1:
                code += between_answers

        code += "\\end{{{0}}}\n".format(answer_format)
        return code

    def __open_question_to_latex(self, quest: OpenQuestion) -> str:
        """returns the latex code of for this question"""
        if quest.n_parts == 0:
            question_format = "openquestion"
        else:
            question_format = "openquestionwithparts"

        code = "\\begin{{{0}}}".format(question_format) + "{\n"
        code += text2latex(quest.question,
                           replace_carriage_returns=False) + "}"
        if self._ts.print_points and quest.points > 0:
            code += "{{{0}}}".format(quest.points) + "{\\droppoints}\n"
        else:
            code += "{}{}\n"
        for txt, points in zip(quest.parts, quest.part_points):
            if points and points > 0:
                code += " \\part[{0}] {{{1}}} \\droppoints\n".format(points,
                                                                     text2latex(txt, replace_carriage_returns=False))
            else:
                code += " \\part {{{0}}}\n".format(text2latex(txt,
                                                              replace_carriage_returns=False))

        code += "\\end{{{0}}}\n".format(question_format)
        return code
