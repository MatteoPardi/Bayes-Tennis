import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # add path/to/bayestennis/../ to sys.path
from bayestennis.create_TennisDataFrame import create_TennisDataFrame


def main ():

    BREAKPOINT_ME = 0

    tdf = create_TennisDataFrame()
    tdf['id_match'] = [1, 2, 3]
    tdf['file_name'] = ['file1', 'file2', 'file3']

    BREAKPOINT_ME = 0


if __name__ == "__main__":

    main()
