import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(sys.path[0], '..', '..', '..')))  # path to bayestennis/../
from bayestennis.io import import_notion_csv
import pandas as pd


def main():

    BREAKPOINT_ME = 0

    file_path = "notion_database_example.csv"

    tdf = import_notion_csv(file_path)

    BREAKPOINT_ME = 0


if __name__ == "__main__":

    main()
