import os
import sys
import time
import asyncio

from run_async import main


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Program needs 1 argument -- Deviantart account name!")
        print("NOTE: account name [title of the user's page] is case-sensitive")
    else:
        account = sys.argv[1]
        try:
            os.mkdir(account)
            os.chdir(account)
            start = time.perf_counter()
            asyncio.run(main(account))
            print(f"scraped in {time.perf_counter() - start} seconds!")
        except FileExistsError:
            print(f"{account} has already been scraped!")
        