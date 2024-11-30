import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(sys.path[0], '..', '..', '..')))  # path to bayestennis/../
from bayestennis.scoring_systems.base import prob_teamA_wins_point, BasicScoreBlock


def main ():

    BREAKPOINT_ME = 0

    abilities = [
        [89, 93],
        [120, 75],
        [89, 100],
        [100, 100],
    ]

    p_teamA_wins_point = prob_teamA_wins_point(abilities)

    score_teamA = [4, 2, 4, 5]
    score_teamB = [2, 4, 0, 4]

    mrdodo_game = BasicScoreBlock(score_end=4, n_max_advantages=1)

    p_this_score = mrdodo_game.prob_this_score(score_teamA, score_teamB, p_teamA_wins_point)
    p_teamA_wins = mrdodo_game.prob_teamA_wins(p_teamA_wins_point)
    p_teamA_wins_without_advantages = mrdodo_game.prob_teamA_wins_without_advantages(p_teamA_wins_point)
    p_teamA_wins_during_advantages_before_deciding_point = mrdodo_game.prob_teamA_wins_during_advantages_before_deciding_point(p_teamA_wins_point)
    p_teamA_wins_at_deciding_point = mrdodo_game.prob_teamA_wins_at_deciding_point(p_teamA_wins_point)

    BREAKPOINT_ME = 0


if __name__ == "__main__":

    main()
