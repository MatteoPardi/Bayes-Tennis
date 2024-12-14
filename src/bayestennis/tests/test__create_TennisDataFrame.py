import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(sys.path[0], '..', '..')))  # path to bayestennis/../
from bayestennis.create_TennisDataFrame import create_TennisDataFrame


def main ():

    BREAKPOINT_ME = 0

    tdf = create_TennisDataFrame()
    tdf['id_match'] = [1, 2, 3]
    tdf['file_name'] = ['file1', 'file2', 'file3']

    BREAKPOINT_ME = 0


if __name__ == "__main__":

    main()
