import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # add path/to/bayestennis/../ to sys.path
from bayestennis.LogLikelihoodTerm import LogLikelihoodTerm
from bayestennis.scoring_systems import MrDodo
import torch


def main():

    BREAKPOINT_ME = 0

    mrdodo = MrDodo()
    mrdodo_logLikelihoodTerm = LogLikelihoodTerm(mrdodo)

    score = [[6, 1, 6, 2, 0, 0]]
    player_indices = [[0, 0, 1, 1]]
    weight = [1.0]

    mrdodo_logLikelihoodTerm.add(score, player_indices, weight)

    abilities_tensor = torch.tensor([100, 100], dtype=torch.float)

    value = mrdodo_logLikelihoodTerm(abilities_tensor)

    BREAKPOINT_ME = 0


if __name__ == "__main__":

    main()
