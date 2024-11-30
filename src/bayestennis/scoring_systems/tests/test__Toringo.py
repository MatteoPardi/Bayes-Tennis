import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(sys.path[0], '..', '..', '..')))  # path to bayestennis/../
from bayestennis.scoring_systems import Toringo


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
        [6, 3, 6, 7, 10, 6],
        [6, 3, 5, 3],
    ]

    toringo = Toringo()

    isValid1, score1 = toringo.check_score(score[0])
    isValid2, score2 = toringo.check_score(score[1])
    isValid3, score3 = toringo.check_score(score[2])
    isValid4, score4 = toringo.check_score(score[3])

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
        [6, 3, 7, 6, 13, 11],
    ]

    p_this_score = toringo.prob_this_score(score_valid, abilities_valid)
    p_teamA_wins = toringo.prob_teamA_wins(abilities_valid)

    p_teamA_wins_100_100 = toringo.prob_teamA_wins([100, 100])
    p_teamA_wins_100_101 = toringo.prob_teamA_wins([100, 101])
    p_teamA_wins_100_102 = toringo.prob_teamA_wins([100, 102])
    p_teamA_wins_100_103 = toringo.prob_teamA_wins([100, 103])
    p_teamA_wins_100_104 = toringo.prob_teamA_wins([100, 104])
    p_teamA_wins_100_105 = toringo.prob_teamA_wins([100, 105])

    BREAKPOINT_ME = 0


if __name__ == "__main__":

    main()
