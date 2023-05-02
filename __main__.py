#!/usr/bin/env python3

import os
import sys
import time
import asyncio
import signal
import argparse

from run_async import main


def on_sigint(signal, frame):
    print("\nSIGINT received. Exiting...")
    sys.exit(0)


def user_confirmation(account):
    while True:
        answer = input(f"The folder '{account}' already exists. Replace contents? [Y/N]: ")
        if answer.upper() == "Y":
            return True
        elif answer.upper() == "N" or answer.upper() != "Y":
            return False


if __name__ == "__main__":
    signal.signal(signal.SIGINT, on_sigint)

    parser = argparse.ArgumentParser(
        description=(
            "A script to download images from a DeviantArt account.\n\n"
            "Example usage without --filetype argument:\n"
            "  __main__.py hyanna-natsu\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("account", help="DeviantArt account name", nargs="?")
    parser.add_argument("--filetype", help="File format of the downloaded images (default: jpg)", default="jpg")
    args = parser.parse_args()

    if not args.account:
        parser.print_help()
        sys.exit(0)

    account = args.account
    file_type = args.filetype

    if os.path.exists(account) and not user_confirmation(account):
        print("Operation canceled.")
        sys.exit(0)

    os.makedirs(account, exist_ok=True)
    os.chdir(account)
    start = time.perf_counter()
    asyncio.run(main(account, file_type))
    print(f"scraped in {time.perf_counter() - start} seconds!")
