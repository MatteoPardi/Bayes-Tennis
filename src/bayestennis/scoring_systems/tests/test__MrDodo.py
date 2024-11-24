import sys
sys.path.insert(0, sys.path[0]+"\\..\\..\\..")
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
        [6, 3, 6, 7, 10, 6],
        [6, 3, 5, 3],
    ]

    mrdodo = MrDodo()

    isValid1, score1 = mrdodo.check_score(score[0])
    isValid2, score2 = mrdodo.check_score(score[1])
    isValid3, score3 = mrdodo.check_score(score[2])
    isValid4, score4 = mrdodo.check_score(score[3])

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

    p_this_score = mrdodo.prob_this_score(score_valid, abilities_valid)
    p_teamA_wins = mrdodo.prob_teamA_wins(abilities_valid)

    p_teamA_wins_100_100 = mrdodo.prob_teamA_wins([[100, 100]])
    p_teamA_wins_100_101 = mrdodo.prob_teamA_wins([[100, 101]])
    p_teamA_wins_100_102 = mrdodo.prob_teamA_wins([[100, 102]])
    p_teamA_wins_100_103 = mrdodo.prob_teamA_wins([[100, 103]])
    p_teamA_wins_100_104 = mrdodo.prob_teamA_wins([[100, 104]])
    p_teamA_wins_100_105 = mrdodo.prob_teamA_wins([[100, 105]])

    BREAKPOINT_ME = 0


if __name__ == "__main__":

    main()
