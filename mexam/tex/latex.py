import os
from subprocess import CalledProcessError, check_output
from typing import List, Optional, Tuple, Union
from ..misc import FILE_ENCODING


def text2latex(text, convert_descriptions=True,
               replace_carriage_returns=True):
    """"converts text (unicode) to latex code
    if wraptext_width is an integer larger than 10, the text will be wrapped
    accordingly.
    """

    LTX_TAB = "\\null\\hspace{2ex}"
    LTX_NEWLINE = "\\\\"
    LTX_PARS = "\\vspace{1ex}" + LTX_NEWLINE
    LTX_UNDERSCORE = "\\_"

    if convert_descriptions:
        text = _convert_enumeration_to_latex(text)
    rtn = text.strip(). \
        replace("\n  ", "\n" + LTX_TAB). \
        replace("_", LTX_UNDERSCORE)

    if replace_carriage_returns:
        rtn = rtn.replace("\n\n", LTX_PARS). \
            replace("\n", LTX_NEWLINE). \
            replace(LTX_NEWLINE, LTX_NEWLINE+"\n")

    return rtn

def _convert_enumeration_to_latex(text, enum_width ="4ex"):
    """ descriptions are defined by <description> text

    Example
    -------
    Consider the following statements:

    <I.> Both rationalists and empiricists do \\underline{not} believe in the notion of innate ideas.

    <II.> Empiricists state that knowledge results from experience.

    Which statement is or which statements are correct or incorrect?
    """

    rtn = ""
    p = 0 # pointer
    while True:
        a = text[p:].find("<") + p
        b = text[a+1:].find(">") + a+1
        c = text[b+1:].find("\n") + b+1
        if a<b<c:
            # pattern found
            rtn += text[p:a]
            rtn += "\\parbox[t]{" + enum_width + "}{\\hfill "+ text[a+1:b] +\
                        "\\hspace{1ex}\\hbox{}}" + "\\parbox[t]{\\textwidth-" +\
                        enum_width + "}{" + text[b+1:c] + "\\vspace{1ex}}\n"
            p = c+1
        else:
            break

    return rtn + text[p:]

# helper
def _shell_command(command:Union[List[str], str], append_output:str="") -> Tuple[bool, str]:
    # command array or string
    if isinstance(command, str):
        command = command.split(" ")
    print("RUNNING: " + " ".join(command))
    try:
        output = check_output(command)  # , stderr=STDOUT
        error = False
    except CalledProcessError as e:
        output = e.output
        error = True

    return error, append_output + str(output)


def run_latex(tex_file:str, latex_cmd:Optional[str],
              latex_cleanup_cmd:Optional[str]=None,
              with_answers:bool=True) -> Tuple[bool, str]:

    if latex_cmd is None or len(latex_cmd)==0:
        return False, ""

    error, output = _shell_command(latex_cmd + " " + tex_file,
                                   append_output="")
    if error:
        return error, output

    if with_answers:
        with open(tex_file, "r", encoding=FILE_ENCODING) as fl:
            tex = fl.read()
        tex = tex.replace("documentclass[", "documentclass[answers,")

        answer_tex_file = os.path.splitext(tex_file)[0] + ".answers.tex"
        with open(answer_tex_file, "w", encoding=FILE_ENCODING) as fl:
            fl.write(tex)
        error, output = _shell_command(latex_cmd + " " + answer_tex_file,
                                       append_output=output)
    else:
        answer_tex_file = None

    if error:
        return error, output

    if latex_cleanup_cmd is not None and len(latex_cleanup_cmd)>0:
        error, output = _shell_command(latex_cleanup_cmd,
                                       append_output=output)

    try:
        os.remove(answer_tex_file) # type: ignore
    except:
        pass

    return error, output
