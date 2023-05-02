import os
import sys
import time
import asyncio
import signal

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

    if len(sys.argv) != 2:
        print("Program needs 1 argument -- Deviantart account name!")
        print("NOTE: account name [title of the user's page] is case-sensitive")
    else:
        account = sys.argv[1]
        if os.path.exists(account) and not user_confirmation(account):
            print("Operation canceled.")
            sys.exit(0)

        os.makedirs(account, exist_ok=True)
        os.chdir(account)
        start = time.perf_counter()
        asyncio.run(main(account))
        print(f"scraped in {time.perf_counter() - start} seconds!")
