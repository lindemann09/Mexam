"""
Command line interface to convert4exam from
Excel file to text file using settings file

usage:
    TODO

"""

import argparse
import sys
from pathlib import Path

from . import Exam, __version__, markdown  # , ExamSettings
from .misc import str_fix_len

#from .tex import LatexFiles, LatexSettings, run_latex

def command_line_interface():
    parser = argparse.ArgumentParser(
        description="Mexam {}: Make exam".format(__version__),
        epilog="(c) O. Lindemann")

    parser.add_argument("DATABASE", help="path to database folder or file")

    subparsers = parser.add_subparsers(dest='cmd')
    cmd_edit = subparsers.add_parser('edit', help ="edit database and its selections and collections") ## database

    # database function
    cmd_edit.add_argument('-I', action='store',
                    dest="ID",
                    help="add selection mark ('XX')  question with a UUID beginning <ID> ")

    cmd_edit.add_argument('-C', action='store',
                    dest='TAG',
                    help="add selection marks ('XX') to questions of the collection <TAG>",
                    default=False)

    cmd_edit.add_argument('-U', action='store',
                    dest="UUID_FILE", metavar="FILE",
                    help="add selection marks ('XX') by UUID file")


    cmd_edit.add_argument("--unselect", dest="unselect_all",
                        action="store_true",
                        help="remove all selection marks ('XX')",
                        default=False)

    cmd_edit.add_argument("--store-collection", dest="NEW_TAG",
                        action="store",
                        help="save current selection as collection with the name <NEW_TAG> and remove all selection marks",
                        default=False)
    cmd_edit.add_argument("--remove-collection", dest="REMOVE_TAG",
                        action="store",
                        help="remove collection from all questions.",
                        default=False)

    cmd_edit.add_argument("--rewrite", dest="rewrite",
                        action="store_true",
                        help="merely rewrite the database (e.g. to format questions or update hashes)",
                        default=False)

    cmd_show = subparsers.add_parser('show', help="show selected questions")
    #cmd_show.add_argument("DATABASE", help="path to database folder or file")
    cmd_show.add_argument('-C', action='store',
                    dest='TAG',
                    help='select collection')
    cmd_show.add_argument('-U', action='store',
                    dest='UUID_FILE', metavar="FILE",
                    help='select by UUID file')
    cmd_show.add_argument("-a", dest="show_all",
                        action="store_true",
                        help="show all, same as `-uztc`",
                        default=False)
    cmd_show.add_argument("-z", dest="hashes",
                        action="store_true",
                        help="show hashes",
                        default=False)
    cmd_show.add_argument("-u",  dest="uuids",
                        action="store_true",
                        help="show short uuids",
                        default=False)
    cmd_show.add_argument("-t",  dest="titles",
                        action="store_true",
                        help="show titles",
                        default=False)
    cmd_show.add_argument("-c",  dest="collections",
                        action="store_true",
                        help="show associates collections",
                        default=False)
    cmd_show.add_argument("-x",  dest="matrix",
                        action="store_true",
                        help="show text matrix",
                        default=False)
    cmd_show.add_argument("-m",  dest="show_markdown",
                        action="store_true",
                        help="show markdown code",
                        default=False)

    cmd_export = subparsers.add_parser('export', help="export selected questions (Exam)") ## database

    #cmd_exam.add_argument("DATABASE", help="path to database folder or file")
    cmd_export.add_argument('-C', action='store',
                    dest='TAG',
                    help='use collection') ## EXAM and INFO

    cmd_export.add_argument('-U', action='store',
                    dest="UUID_FILE", metavar="FILE",
                    help='use selection from UUID file') ## EXAM and INFO

    cmd_export.add_argument('--md', action='store',
                    dest='exam_export', metavar="FILE",
                    help='export exam to markdown file')

    cmd_export.add_argument('--uuids', action='store',
                    dest='uuid_export', metavar="FILE",
                    help='export uuids of exam')

    cmd_export.add_argument("-i", dest="quest_info",
                        action="store_true",
                        help="include question info",
                        default=False)
    cmd_export.add_argument("-l", dest="quest_label",
                        action="store_true",
                        help="use question labels instead language indicators",
                        default=False)

    args = parser.parse_args()

    try:
        db_path = Path(args.DATABASE)
    except TypeError:
        info_exit("Please specify a database file or folder")

    db = markdown.load_database(db_path)

    ## EDIT
    if args.cmd == "edit":

        rewrite = args.rewrite
        if args.TAG or args.UUID_FILE or args.ID:
            # add selection
            if args.unselect_all:
                info_exit("You can't add a selection and unselect all.")
            elif args.NEW_TAG:
                info_exit("You can't add a selection and store a collection in one step.")
            elif args.TAG and ask_yes_no(
                    f"Add selection mark ('XX') to all items of the collection '{args.TAG}'"):
                db.select_collection(tag=args.TAG, keep_selected=True)
                rewrite = True
            elif args.UUID_FILE and ask_yes_no(
                    f"Add selection mark to all items listed in the uuid_file '{args.UUID_FILE}'"):
                uuids, _ = Exam.load_uuid_file(args.UUID_FILE)
                db.select_uuids(uuids=uuids, keep_selected=True)
                rewrite = True
            elif args.ID:
                try:
                    found = db.add_selection_uuid(args.ID)
                except RuntimeError as er:
                    print(f"ERROR: {er}")
                    exit()
                if found:
                    rewrite = True
                else:
                    print(f"Can't find UUID '{args.ID}'")
                    exit()
            else:
                exit()

        if args.NEW_TAG:
            if ask_yes_no(f"Save current selection as collection '{args.NEW_TAG}'"):
                db.store_collection(tag=args.NEW_TAG)
                rewrite = True
            else:
                exit()
        elif args.REMOVE_TAG:
            if ask_yes_no(f"Remove collection '{args.REMOVE_TAG}' from all items"):
                db.remove_collection(tag=args.REMOVE_TAG)
                rewrite = True
            else:
                exit()

        if args.unselect_all:
            if ask_yes_no("Unselect all selected questions"):
                db.unselect_all()
                rewrite = True
            else:
                exit()

        print(f"- selected: {db.n_selected}")
        if rewrite:
            print(f"** Rewrite {db_path} **")
            markdown.save_database_folder(db, db_path)
        else:
            info_exit(" ")

    ## SHOW
    elif args.cmd == "show":
        if args.show_all:
            args.uuids = True
            args.hashes = True
            args.collections = True
            args.titles = True

        exam = Exam(db,
                    select_collection=args.TAG,
                    uuid_file=args.UUID_FILE)
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
            for i, (top, u, t, h, c) in enumerate(zip(exam.topics(), exam.short_uuids(), exam.titles(), hashes, coll)):
                txt = f" {i+1:2d}) "
                if args.uuids:
                    txt += f" {u} ..,"
                if args.hashes:
                    txt += f" {h},"
                if args.collections:
                    # show collections, first selected collection
                    s = c.replace(",", "")
                    if args.TAG:
                        s = s.replace(args.TAG, "").replace("  ", " ").strip()
                        s = f"{args.TAG} {s}"
                    txt += f" {str_fix_len(s.strip(), length=20)},"

                txt += f" {str_fix_len(top, length=24, cut_left=False)},"
                if args.titles:
                    txt += f" {t},"
                print(txt[:-1])

        if args.show_markdown:
            print(markdown.database_to_markdown(exam))

    ## EXPORT
    elif args.cmd == "export":

        exam = Exam(db,
                    select_collection=args.TAG,
                    uuid_file=args.UUID_FILE,
                    quest_info=args.quest_info,
                    question_label=args.quest_label)
        if exam.n_questions == 0:
            info_exit("No questions defined. Use selection marker, collection tag or uuid file.")

        if not args.exam_export and not args.uuid_export:
            ## default
            # Ask user for filename
            filename = input("Enter the exam name: ")
            args.exam_export = Path(filename).with_suffix('.md')
            args.uuid_export = Path(filename).with_suffix('.uuid')
            exam.question_label = True
            exam.quest_info = False

        if args.exam_export:
            print(f"save {args.exam_export}")
            markdown.save_markdown_file(exam, args.exam_export)
        if args.uuid_export: ## uuids
            print(f"save {args.uuid_export}")
            exam.save_uuid_file(file_path=args.uuid_export)

    else:
        db.print_summary()
        db.print_collections_selections()

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