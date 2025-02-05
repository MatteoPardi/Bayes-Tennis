import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # add path/to/bayestennis/../ to sys.path
from bayestennis.scoring_systems import MrDodo


def main ():

    BREAKPOINT_ME = 0

    abilities = [
        [89, 93],
        [120, 75],
        [89, 100],
        [100, 100],
    ]

    score = [
        [6, 1, 6, 2],
        [6, 3, 6, 7],
        [6, 3, 6, 7, 6, 10],
        [6, 3, 5, 3],
    ]

    mrdodo = MrDodo()

    isValid1, score1, winner1 = mrdodo.process_score(score[0])
    isValid2, score2, winner2 = mrdodo.process_score(score[1])
    isValid3, score3, winner3 = mrdodo.process_score(score[2])
    isValid4, score4, winner4 = mrdodo.process_score(score[3])

    abilities_valid = [
        [89, 93],
        [120, 75],
        [89, 100],
        [100, 100],
    ]

    score_valid = [
        [6, 1, 6, 2, 0, 0],
        [6, 3, 7, 6, 0, 0],
        [6, 3, 6, 7, 10, 6],
        [6, 3, 1, 6, 11, 13],
    ]

    p_this_score = mrdodo.prob_this_score(score_valid, abilities_valid)
    p_teamA_wins = mrdodo.prob_teamA_wins(abilities_valid)

    p_teamA_wins_100_100 = mrdodo.prob_teamA_wins([100, 100])
    p_teamA_wins_100_101 = mrdodo.prob_teamA_wins([100, 101])
    p_teamA_wins_100_102 = mrdodo.prob_teamA_wins([100, 102])
    p_teamA_wins_100_103 = mrdodo.prob_teamA_wins([100, 103])
    p_teamA_wins_100_104 = mrdodo.prob_teamA_wins([100, 104])
    p_teamA_wins_100_105 = mrdodo.prob_teamA_wins([100, 105])

    BREAKPOINT_ME = 0


if __name__ == "__main__":

    main()
