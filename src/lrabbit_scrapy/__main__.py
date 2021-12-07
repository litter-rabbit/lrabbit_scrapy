from .command import run
import sys

if __name__ == '__main__':
    args =sys.argv[1:]
    run(*args)
