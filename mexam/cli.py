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
#from .misc import  make_filename
from . import  markdown,  Exam   #, ExamSettings
#from .tex import LatexFiles, LatexSettings, run_latex

def command_line_interface():
    parser = argparse.ArgumentParser(
        description="Mexam {}: Make exam".format(__version__),
        epilog="(c) O. Lindemann")

    parser.add_argument("DATABASE", help="path to database folder or file")

    subparsers = parser.add_subparsers(dest='cmd')
    cmd_db = subparsers.add_parser('db') ## database

    # database function
    cmd_db.add_argument("--rewrite", dest="rewrite",
                        action="store_true",
                        help="rewrite database",
                        default=False)
    cmd_db.add_argument("--unselect", dest="unselect_all",
                        action="store_true",
                        help="unselect all questions",
                        default=False)
    cmd_db.add_argument("--store-collection", dest="NEW_TAG",
                        action="store",
                        help="save current selection as collection with the name <TAG> and unselect all.",
                        default=False)
    cmd_db.add_argument("--add-selection", dest="TAG_ADD",
                        action="store",
                        help="add a selection mark ('XX') to all question of the collection <TAG_ADD>",
                        default=False)


    cmd_save = subparsers.add_parser('save') ## database
    #cmd_exam.add_argument("DATABASE", help="path to database folder or file")
    cmd_save.add_argument('--md', action='store',
                    dest='exam_file',
                    help='save exam to markdown file')

    cmd_save.add_argument('--uuids', action='store',
                    dest='file',
                    help='save uuids of exam')

    cmd_save.add_argument('-S', action='store',
                    dest='tag',
                    help='select collection') ## EXAM and INFO

    cmd_save.add_argument('-U', action='store',
                    dest="uuid_file",
                    help='select by UUID file') ## EXAM and INFO

    cmd_save.add_argument("-i", dest="quest_info",
                        action="store_true",
                        help="include question info",
                        default=False)
    cmd_save.add_argument("-l", dest="quest_label",
                        action="store_true",
                        help="use question labels instead language indicators",
                        default=False)

    cmd_show = subparsers.add_parser('show') ## database
    #cmd_show.add_argument("DATABASE", help="path to database folder or file")
    cmd_show.add_argument('-S', action='store',
                    dest='tag',
                    help='select collection')
    cmd_show.add_argument('-U', action='store',
                    dest='uuid_file',
                    help='select by UUID file')
    cmd_show.add_argument("-s", dest="hashes",
                        action="store_true",
                        help="show hashes",
                        default=False)
    cmd_show.add_argument("-u",  dest="uuids",
                        action="store_true",
                        help="show uuids",
                        default=False)
    cmd_show.add_argument("-t",  dest="titles",
                        action="store_true",
                        help="show titles",
                        default=False)
    cmd_show.add_argument("-c",  dest="collections",
                        action="store_true",
                        help="show associates collections",
                        default=False)
    cmd_show.add_argument("-m",  dest="matrix",
                        action="store_true",
                        help="show text matrix",
                        default=False)
    cmd_show.add_argument("-M",  dest="show_markdown",
                        action="store_true",
                        help="show markdown code",
                        default=False)
    ## misc
    #parser.add_argument("--example-settings", dest="examplefile",
    #                action="store_true",
    #                help="print example settings file",
    #                default=False)

    args = parser.parse_args()

    #if args.examplefile:
    #    print("---")
    #    print(ExamSettings.EXAMPLE)
    #    print(LatexSettings.EXAMPLE)
    #    print("...")
    #    sys.exit()

    try:
        db_path = Path(args.DATABASE)
    except TypeError:
        info_exit("Please specify a database file or folder")

    db = markdown.load_database(db_path)

    if args.cmd == "db":
        if args.TAG_ADD:
            # add selection
            if args.unselect_all:
                info_exit("You can't add a selection and unselect all.")
            elif args.NEW_TAG:
                info_exit("You can't add a selection and store a collection in one step.")
            elif ask_yes_no(f"Add selection mark ('XX') to all items of the collection '{args.TAG_ADD}'"):
                db.set_collection(tag=args.TAG_ADD)
            else:
                exit()

        if args.NEW_TAG:
            if ask_yes_no(f"Save current selection as collection '{args.NEW_TAG}'"):
                db.set_collection(tag=args.NEW_TAG)
            else:
                exit()
            db.store_collection(tag=args.NEW_TAG)

        if args.unselect_all:
            if ask_yes_no("Unselect all selected questions"):
                db.unselect_all()
            else:
                exit()

        db.print_summary()

        if args.rewrite or args.NEW_TAG or args.TAG_ADD or args.unselect_all:
            print(f"** Rewrite {db_path} **")
            markdown.save_database_folder(db, db_path)
        else:
            info_exit(" ")

    elif args.cmd == "show":
        exam = Exam(db,
                    select_collection=args.tag,
                    uuid_file=args.uuid_file)
        exam.print_summary()

        # print info
        if args.titles or args.uuids or args.hashes or args.collections:
            hashes = exam.get_short_hashes_bilingual()
            if len(hashes["L1"]) > 0:
                # is bilingual
                hashes = [f"{x}, {y}" for x,y in zip(hashes["L1"], hashes["L2"])]
            else:
                hashes = list(exam.question_hash_list)

            coll = [x.collection_string for x in exam.questions]
            for i, (top, u, t, h, c) in enumerate(zip(exam.topics(), exam.uuids(), exam.titles(), hashes, coll)):
                txt = f" {i+1:2d}) "
                if args.uuids:
                    txt += f" {u},"
                if args.hashes:
                    txt += f" {h},"
                txt += f" {top},"
                if args.titles:
                    txt += f" {t},"
                if args.collections:
                    txt += f" [{c}],"
                print(txt[:-1])

        if args.show_markdown:
         print(markdown.database_to_markdown(exam))

    elif args.cmd == "save":
        exam = Exam(db,
                    select_collection=args.tag,
                    uuid_file=args.uuid_file,
                    quest_info=args.quest_info,
                    question_label=args.quest_label)
        if args.exam_file:
            markdown.save_markdown_file(exam, args.exam_file)
        elif args.file: ## uuids
            exam.save_uuid_file(file_path=args.file)
        else:
            info_exit("Please define either markdown or uuids destination file.")

    else:
        db.print_summary()
        info_exit(" ")

## helper
def ask_yes_no(question:str, default_answer:bool =False):
    reply = str(input(question + ' (yes/no): ')).lower().strip()
    if reply[:1] == 'y':
        return True
    elif reply[:1] == 'n':
        return False
    else:
        return default_answer

def info_exit(feedback:str):
    print(feedback)
    print("Use -h for help")
    sys.exit()