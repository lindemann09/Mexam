"""Text converter functions and Latex Code"""
from pathlib import Path
from hashlib import md5
from random import shuffle
from typing import List, Optional
from time import ctime

FILE_ENCODING = "utf-8"

def shuffle_fixed_positions(element_list, fixed_elements=()):
    """shuffel list with some elements at a fixed position

    all elements must be unique
    """

    variable_ids = []
    fixed_ids = []
    for i, elm in enumerate(element_list):
        if elm in fixed_elements:
            fixed_ids.append(i)
        else:
            variable_ids.append(i)

    shuffle(variable_ids)

    new_order = []
    for i, elm in enumerate(element_list):
        if i in fixed_ids:
            new_order.append(elm)
        else:
            new_order.append(element_list[variable_ids.pop()])

    return new_order


def long_hash(content):
    return md5(content.encode(FILE_ENCODING, 'replace')).hexdigest()


def short_hash(content):
    return long_hash(content)[:6]

def make_filename(name, suffix:str, addional_suffix:Optional[str]=None)->str:
    """returns filename and question filename"""

    if addional_suffix is None:
        rtn = name
    else:
        rtn = name + "_" + addional_suffix

    return rtn + suffix

def underline(text, line_type="="):
    return "{}\n{}".format(text, str(line_type * len(text)))

def bool_str(bool):
    if bool:
        return "TRUE"
    else:
        return "FALSE"

def strip_lines(txt:str):
    """strips each line and keeps empty lines only in between text"""
    rtn = ""
    for x in txt.splitlines():
        rtn += x.strip() + "\n"
    return rtn.rstrip()


def write_if_different(file_path: Path, content: str):
    """rewrites the file if the content is different"""
    if file_path.is_file():
        with open(file_path, "r", encoding=FILE_ENCODING) as fl:
            fl_content = fl.read()
        if hash(fl_content) == hash(content):
            return # don't write
    # rewrite
    with open(file_path, "w", encoding=FILE_ENCODING) as fl:
        fl.write(content)

class MultiCounter(object):

    def __init__(self):
        self.dict = {}

    def inc(self, label):
        try:
            self.dict[label] += 1
        except KeyError:
            self.dict[label] = 1

    def get(self, label) -> int:
        try:
            return self.dict[label]
        except KeyError:
            return 0

def all_files(path: Path, suffix: str) -> List[Path]:
    return [fl for fl in path.iterdir() if fl.is_file() and fl.suffix == suffix]

def number_to_string(num):
    """convert number to string with decimals only if needed"""
    # Check if the number is an integer
    if num == int(num):
        return str(int(num))
    else:
        return str(num)


class LogFile(object):

    def __init__(self, filename="mexam.log"):

        self.file = open(filename, 'a', encoding=FILE_ENCODING)

    def __del__(self):

        try:
            self.file.close()
        except AttributeError:
            pass

    def log(self, txt):

        for row in txt.split("\n"):
            row = row.rstrip()
            if len(row) > 0:
                self.file.write("[{}] {}\n".format(ctime()[4:19], row))
                print(row)
