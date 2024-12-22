import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # add path/to/bayestennis/../ to sys.path
from bayestennis.TennisUniverse import TennisUniverse
from bayestennis.io import import_notion_csv
import matplotlib.pyplot as plt


def main():

    BREAKPOINT_ME = 0

    file_path = str(Path(__file__).resolve().parent / "notion_database_example.csv")
    tdf = import_notion_csv(file_path)

    tu = TennisUniverse(tdf)

    optimization_info = tu.optimize()

    plt.figure()
    plt.plot(optimization_info['idx_iteration'], optimization_info['loss'])
    plt.xlabel("Iteration")
    plt.ylabel("Loss")
    plt.show()

    BREAKPOINT_ME = 0


if __name__ == "__main__":

    main()
