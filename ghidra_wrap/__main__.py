import argparse
import logging
import os

from .ghidra_wrap import GhidraWrap, GhidraWrapOptions

def main():
    args = argparse.ArgumentParser(prog="ghidra_wrap", description="Painless Wrapper for Ghidra Headless")
    args.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    args.add_argument("-l", "--list", action="store_true", help="list projects and analyzed files")
    args.add_argument("-t", "--timeout", nargs="?", type=int, help="analysis timeout in seconds")
    args.add_argument("--project", nargs="?", help="project name [default: defproj]")
    args.add_argument("binary", nargs="?", help="file to analyze")
    args.add_argument("script", nargs="?", help="script to run")
    args.add_argument("script_arguments", nargs="*", help="script args")

    args = args.parse_args()

    if args.project is None:
        args.project = "defproj"

    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.DEBUG
    logging.basicConfig(format="%(name)s::%(levelname)s : %(message)s", level=log_level)

    opt = GhidraWrapOptions()
    if args.timeout:
        opt.timeout = args.timeout

    gw = GhidraWrap(opt=opt)
    if not gw.project_exists(args.project):
        try:
            gw.create_project(args.project)
        except ValueError as e:
            print("!Err:", str(e))

    if args.list:
        for proj in gw.list_projects():
            print("project", proj)
            files = gw.list_files_in_project(proj)
            if files:
                print("\t", " ".join(files))

    if args.binary:
        print("[+] Analyzing", args.binary)
        if os.path.basename(args.binary) not in gw.list_files_in_project(args.project):
            try:
                gw.analyze_file(args.project, args.binary)
            except ValueError as e:
                print("!Err:", str(e))

    if args.script:
        print("[+] Running script", args.script)
        try:
            gw.run_script(args.project, args.binary, args.script, *args.script_arguments)
        except ValueError as e:
            print("!Err:", str(e))

if __name__ == "__main__":
    main()
