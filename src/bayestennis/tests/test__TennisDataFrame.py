import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(sys.path[0], '..', '..')))  # path to bayestennis/../
from bayestennis.TennisDataFrame import TennisDataFrame


def main ():

    BREAKPOINT_ME = 0

    tdf = TennisDataFrame()
    tdf['id_match'] = [1, 2, 3]
    tdf['file_name'] = ['file1', 'file2', 'file3']

    BREAKPOINT_ME = 0


if __name__ == "__main__":

    main()
