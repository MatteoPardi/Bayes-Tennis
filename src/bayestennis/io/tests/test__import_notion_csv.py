import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # add path/to/bayestennis/../ to sys.path
from bayestennis.io import import_notion_csv
import pandas as pd


def main():

    BREAKPOINT_ME = 0

    file_path = str(Path(__file__).resolve().parent / "notion_database_example.csv")

    tdf = import_notion_csv(file_path)

    BREAKPOINT_ME = 0


if __name__ == "__main__":

    main()
