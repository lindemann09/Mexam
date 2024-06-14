from os import path
from ..misc import FILE_ENCODING

def create_make_exam_r_script(files, name, directory):
    # make_exam file
    scr = "library(exams)\n"
    for lang in files.keys():
        lst = ",\n".join([repr(x) for x in files[lang]])
        scr += _REXAM_SCRIPT.format(lst, repr(name + "-" + lang))
    flname = path.join(directory, "make_exam.R")
    with open(flname, "w", encoding=FILE_ENCODING) as fl:
        fl.write(scr)


def create_qti_export_r_script(files, directory):
    lst = ""
    for lang in files.keys():
        lst += ",\n".join([repr(x) for x in files[lang]]) + ",\n\n"

    flname = path.join(directory, "qti_export.R")
    with open(flname, "w", encoding=FILE_ENCODING) as fl:
        fl.write(_REXAM_SCRIPT_QTI_EXPORT.format(lst[:-3]))


_REXAM_SCRIPT = """
files = c({})
exams2pdf(file = files,
           name = {},
           solution = FALSE,
           mathjax = TRUE,
           dir=".",
           edir = ".")

"""

_REXAM_SCRIPT_QTI_EXPORT = """library(exams)

files = c({})

titles = lapply(files, function(x) substr(x, 0, nchar(x)-4))
mchoice_make <- function(x) {{
  make_itembody_qti21(shuffle = x$metainfo$shuffle,
                      enumerate = FALSE)(x)
}}

exams2qti21(file=files, ititle=titles, mchoice = mchoice_make)
"""
