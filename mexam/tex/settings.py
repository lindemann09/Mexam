"""Text function and Latex Code"""
from typing import Optional, Tuple
from .. import misc
from ..abc_settings import ABCSettings


class LatexSettings(ABCSettings):

    EXAMPLE = """# latex settings
date: 19--12--2019
course_title: Concepts and Categories
course_code: FSWP4--0033--B
use_letters: True
print_points: True
exam_title_lang1: Exam
exam_title_lang2: Exam Dutch
page_counter: 2
latex_cmd: latexmk -lualatex
latex_cleanup_cmd: latexmk -c"""

    def __init__(self, filename: str | None = None, parent: ABCSettings | None = None):
        super().__init__(filename, parent)

        self.date = self._optional("date", default=None)
        self.course_title = self._optional("course_title", default=None)
        self.course_code = self._optional("course_code", default=None)
        self.exam_title = [self._optional("exam_title_lang1", default=None),
                           self._optional("exam_title_lang2", default="")]
        self.page_counter = self._optional("page_counter", default=1)

        self.language1_filename_suffix = None
        self.language2_filename_suffix= None
        self.print_hashes = False

    def set(self, language1_filename_suffix:str,
                 language2_filename_suffix:Optional[str],
                 print_hashes:bool,
                 ask_if_undef:bool):
        """Tex converter"""

        self.language1_filename_suffix = language1_filename_suffix
        self.language2_filename_suffix= language2_filename_suffix
        self.print_hashes = print_hashes

        if ask_if_undef:
            self.date = _askfor("  Date : ", self.date)
            self.course_title = _askfor("  Course title: ", self.course_title)
            self.course_code = _askfor("  Course code: ", self.course_code)
            self.exam_title[0] = _askfor("\n  Exam title (e.g. 'Exam'): ",
                                    self.exam_title[0])
            if self.is_multi_language:
                self.exam_title[1] = _askfor("\n Exam type in the second language "
                                            "(e.g. 'Tentamen'): ",
                                            self.exam_title[1])

            if self.page_counter is None:
                yn = input("  Should the page counter start with 1? (Y/n)")
                if not len(yn) == 0 and yn.lower() != "y" and yn.lower() != "yes":
                    while self.page_counter is None:
                        try:
                            self.page_counter = int(input("  Set counter: "))
                        except ValueError:
                            pass
                else:
                    self.page_counter = 1

    @property
    def use_letters(self):
        return self._optional("use_letters", default=True)

    @property
    def latex_cmd(self):
        return self._optional("latex_cmd", default=None)

    @property
    def latex_cleanup_cmd(self):
        return self._optional("latex_cleanup_cmd", default=None)

    @property
    def print_points(self):
        return self._optional("print_points", default=False)

    @property
    def tex_file(self) -> Tuple[str, str]:

        lang1 = misc.make_filename(self.name, ".tex",
                                addional_suffix=self.language1_filename_suffix)
        if self.language2_filename_suffix is not None:
            lang2 = misc.make_filename( self.name, ".tex",
                                addional_suffix=self.language2_filename_suffix)
        else:
            lang2 = ""
        return lang1, lang2

    @property
    def quest_file(self) -> Tuple[str, str]:
        lang1 = misc.make_filename(self.name, ".quest",
                                addional_suffix=self.language1_filename_suffix)
        if self.language2_filename_suffix is not None:
            lang2 = misc.make_filename( self.name, ".quest",
                                addional_suffix=self.language2_filename_suffix)
        else:
            lang2 = ""
        return lang1, lang2

    @property
    def is_multi_language(self) -> bool:
        return self.language1_filename_suffix is not None and \
                             self.language2_filename_suffix is not None

# ----------- helper functions
def _askfor(question, value):
    while value is None or len(value)<1:
        value = input(question)
    return value



