"""
Command line interface to convert4exam from
Excel file to text file using settings file

usage:
    TODO

"""

import argparse
import sys

from pathlib import Path

from . import __version__
from .misc import  make_filename
from . import  markdown,  Exam, ExamSettings
from .tex import LatexFiles, LatexSettings, run_latex

def command_line_interface():
    parser = argparse.ArgumentParser(
        description="Mexam {}: Make exam".format(__version__),
        epilog="(c) O. Lindemann")
    parser.add_argument("DATABASE", nargs='?', default=None,
                        help="the path to database folder or file")

    parser.add_argument('-s', action='store',
                    dest='tag',
                    help='Select collection')

    parser.add_argument('-u', action='store',
                    dest='uuid_file',
                    help='UUID file')


    parser.add_argument("-e", action='store',
                        dest='exam_file',
                        help="exam file name",
                        default=False)
    parser.add_argument("-i", dest="quest_info",
                        action="store_true",
                        help="include question info",
                        default=False)
    parser.add_argument("-l", dest="quest_label",
                        action="store_true",
                        help="use question labels instead language indicators",
                        default=False)

    parser.add_argument("-R", "--rewrite", dest="rewrite",
                        action="store_true",
                        help="rewrite database",
                        default=False)
    parser.add_argument("--example-settings", dest="examplefile",
                        action="store_true",
                        help="print example settings file",
                        default=False)
    parser.add_argument("--hash_codes", dest="hashes",
                        action="store_true",
                        help="show hashes",
                        default=False)
    parser.add_argument("--label_list", dest="hashes",
                        action="store_true",
                        help="show labels",
                        default=False)
    parser.add_argument("--test_matrix", dest="matrix",
                        action="store_true",
                        help="show text matrix",
                        default=False)

    # database function
    parser.add_argument("--unselect", dest="unselect_all",
                        action="store_true",
                        help="unselect all questions (to save in DB use '-R')",
                        default=False)

    parser.add_argument("--info", dest="info",
                        action="store_true",
                        help="database info",
                        default=False)


    args = parser.parse_args()

    if args.examplefile:
        print("---")
        print(ExamSettings.EXAMPLE)
        print(LatexSettings.EXAMPLE)
        print("...")
        sys.exit()

    try:
        db_path = Path(args.DATABASE)
    except TypeError:
        print("Please specify a database file or folder")
        print("Use -h for help")
        sys.exit()

    db = markdown.load_database(db_path)
    if args.info:
        db.unselect_all()
        db.print_summary()
        exit()

    if args.unselect_all:
        db.unselect_all()

    if args.rewrite:
        print(f"rewrite {db_path}")
        markdown.save_database_folder(db, db_path)

    exam = Exam(db,
                select_collection=args.tag,
                uuid_file=args.uuid_file,
                quest_info=args.quest_info,
                question_label=args.quest_label)
    exam.print_summary()
    if args.exam_file:
        markdown.save_markdown_file(exam, args.exam_file,)


