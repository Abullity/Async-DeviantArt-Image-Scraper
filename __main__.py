import sys
import time

from run_threadpool import get_urls


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Program needs 1 argument -- Deviantart account name!")
        print("NOTE: account name [title of the user's page] is case-sensitive")
    else:
        account = sys.argv[1]

        start = time.perf_counter()
        get_urls(account)
        print(f"scraped in {time.perf_counter() - start} seconds!")

        