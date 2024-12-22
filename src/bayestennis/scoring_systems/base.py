from typing import Optional, Union, Sequence, Tuple
import torch
from scipy.special import binom
from math import pi
from ..utils import as_torch_tensor


def prob_teamA_wins_point (abilities: Union[torch.Tensor, Sequence[float]]) -> torch.Tensor:
    """
    Heuristic formula to estimate the probability of team A winning a point given the abilities of players

    Usage example:
        # Case: match type = single
        abilities = [89, 93]
        p_teamA_wins_point = prob_teamA_wins_point(abilities)
        # Case: match type = double
        abilities = [89, 93, 89, 93]
        p_teamA_wins_point = prob_teamA_wins_point(abilities)

    Args:
        abilities : torch.Tensor[torch.float] (n_batches, 2) or (n_batches, 4)
            abilities of players. The last dimension must be in [2, 4]:
                - 2: match type = single
                - 4: match type = double

    Returns:
        p_teamA_wins_point : torch.Tensor[torch.float] (n_batches,)
            Probability of team A winning a point, computed using the heuristic formula
    """

    # As torch tensor
    abilities = as_torch_tensor(abilities, torch.float)

    # Checks
    assert abilities.shape[-1] in [2, 4], "abilities.shape[-1] must be 2 (single) or 4 (double)"
    assert abilities.ndim in [1, 2], "abilities.shape must be (2,), (4,), (n_batches, 2) or (n_batches, 4)"

    # Define the utlity vector u based on match type
    if abilities.shape[-1] == 2:  # Case: match type = single
        u = torch.tensor([1., -1.], device=abilities.device)
    elif abilities.shape[-1] == 4:  # Case: match type = double
        u = torch.tensor([0.5, 0.5, -0.5, -0.5], device=abilities.device)
    
    # Heuristic formula
    p_teamA_wins_point = 0.5 + torch.atan(0.1 * abilities @ u) / pi

    return p_teamA_wins_point


class BasicScoreBlock:
    """
    Basic score block representation for probability calculations

    Attributes:
        score_end : int
            Score threshold to end the game.
        n_max_advantages : int | None
            Maximum number of advantages allowed. None represents infinite advantages.
        device : torch.device
            Device to store tensors on

    Methods:
        to(device)
        prob_this_score(score_teamA, score_teamB, p_teamA_wins_point, p_teamA_wins_deciding_point=None)
        prob_teamA_wins(p_teamA_wins_point, p_teamA_wins_deciding_point=None)
        prob_teamA_wins_without_advantages(p_teamA_wins_point)
        prob_teamA_wins_during_advantages_before_deciding_point(p_teamA_wins_point)
        prob_teamA_wins_at_deciding_point(p_teamA_wins_point, p_teamA_wins_deciding_point)
    """


    def __init__ (self, score_end: int, n_max_advantages: Optional[int] = None, device: torch.device = torch.device("cpu")) -> None:
        """
        Basic score block representation for probability calculations

        Args:
            score_end : int
                Score threshold to end the game.
            n_max_advantages : int | None = None
                Maximum number of advantages allowed. Defaults to None (infinite advantages).
            device : torch.device = torch.device("cpu")
                Device to store tensors on. Defaults to CPU.
        """

        self.score_end = score_end
        self.n_max_advantages = n_max_advantages
        self.device = device

        # Precompute utility binomial coefficients
        self._utils_binom = torch.tensor(
            [binom(score_end - 1 + n, score_end - 1) for n in range(score_end)]
        ).float().to(device)


    def to (self, device: torch.device) -> None:
        """
        Move the internal tensors to a specified device.

        Args:
            device : torch.device
                Device to move the tensors to
        """

        if self.device != device:
            self.device = device
            self._utils_binom = self._utils_binom.to(device)


    def prob_this_score (
            self,
            score_teamA: Union[torch.Tensor, Sequence[int]],
            score_teamB: Union[torch.Tensor, Sequence[int]],
            p_teamA_wins_point: Union[torch.Tensor, Sequence[float]],
            p_teamA_wins_deciding_point: Optional[Union[torch.Tensor, Sequence[float]]] = None
        ) -> torch.Tensor:
        """
        Compute the probability of a given score

        Args;
            score_teamA : torch.Tensor[torch.long] (n_batches,)
                Scores of team A.
            score_teamB : torch.Tensor[torch.long] (n_batches,)
                Scores of team B.
            p_teamA_wins_point : torch.Tensor[torch.float] (n_batches,)
                Probability of team A winning a point.
            p_teamA_wins_deciding_point : torch.Tensor[torch.float] | None = None
                Probability of team A winning the deciding point. Set to None to use p_teamA_wins_point.

        Returns:
            p_this_score : torch.Tensor[torch.float]. (n_batches,)
                Probability of the given score.
        """

        # As torch tensor
        score_teamA = as_torch_tensor(score_teamA, torch.long, device=self.device)
        score_teamB = as_torch_tensor(score_teamB, torch.long, device=self.device)
        p_teamA_wins_point = as_torch_tensor(p_teamA_wins_point, torch.float, device=self.device)
        if p_teamA_wins_deciding_point is not None:
            p_teamA_wins_deciding_point = as_torch_tensor(p_teamA_wins_deciding_point, torch.float, device=self.device)
        else:
            p_teamA_wins_deciding_point = p_teamA_wins_point

        # Checks
        assert score_teamA.ndim == 1, "score_teamA.shape must be (n_batches,)"
        assert score_teamB.ndim == 1, "score_teamB.shape must be (n_batches,)"
        assert p_teamA_wins_point.ndim == 1, "p_teamA_wins_point.shape must be (n_batches,)"
        if p_teamA_wins_deciding_point is not None:
            assert p_teamA_wins_deciding_point.ndim == 1, "p_teamA_wins_deciding_point.shape must be (n_batches,)"
        assert score_teamA.shape == score_teamB.shape, "score_teamA.shape must be equal to score_teamB.shape"
        assert score_teamA.shape == p_teamA_wins_point.shape, "score_teamA.shape must be equal to p_teamA_wins_point.shape"
        if p_teamA_wins_deciding_point is not None:
            assert score_teamA.shape == p_teamA_wins_deciding_point.shape, "score_teamA.shape must be equal to p_teamA_wins_deciding_point.shape"
        
        # Utility quantities:
        #     e1 = self.score_end - 1
        #     deciding_point_was_played = boolean mask
        #     minmin = min(min(score_teamA, score_teamB), e1)
        #     maxmin = max(min(score_teamA, score_teamB), e1)
        e1 = self.score_end - 1
        minmin = torch.minimum(score_teamA, score_teamB)
        maxmin = minmin*1
        if self.n_max_advantages is None: pass
        else: deciding_point_was_played = (minmin == e1+self.n_max_advantages)
        minmin[minmin > e1] = e1 
        maxmin[maxmin < e1] = e1

        # Compute probability of the input score
        # Note: (score_teamA, score_teamB)=(0, 0) --> prob_this_score=1
        if self.n_max_advantages is None:  # Full advantages
            p_this_score = self._utils_binom[minmin] * 2**(maxmin-e1) * p_teamA_wins_point**score_teamA * (1-p_teamA_wins_point)**score_teamB
        else:  # Advantages from 0 up to n_max_advantages
            has_teamA_won = (score_teamA > score_teamB)
            p_this_score = \
                self._utils_binom[minmin] * 2**(maxmin-e1) * ( \
                # Case 1: deciding point was not played
                (~deciding_point_was_played) * p_teamA_wins_point**score_teamA * (1-p_teamA_wins_point)**score_teamB + \
                # Case 2: deciding point was played
                deciding_point_was_played * (p_teamA_wins_point*(1-p_teamA_wins_point))**maxmin * ( \
                # Case 2.1: team A won the deciding point
                has_teamA_won * p_teamA_wins_deciding_point + \
                # Case 2.2: team B won the deciding point
                (~has_teamA_won) * (1-p_teamA_wins_deciding_point)) \
            )

        return p_this_score

          
    def prob_teamA_wins (
            self, 
            p_teamA_wins_point: Union[torch.Tensor, Sequence[float]],
            p_teamA_wins_deciding_point: Optional[Union[torch.Tensor, Sequence[float]]] = None
        ) -> torch.Tensor:
        """
        Compute the probability of team A winning

        Args:
            p_teamA_wins_point : torch.Tensor[torch.float] (n_batches,)
                Probability of team A winning a point.
            p_teamA_wins_deciding_point : torch.Tensor[torch.float] (n_batches,) | None = None
                Probability of team A winning the deciding point. Defaults to None, which implies
                using p_teamA_wins_point as p_teamA_wins_deciding_point

        Returns:
            p_teamA_wins : torch.Tensor[torch.float] (n_batches,)
                Probability of team A winning.
        """

        # As torch tensor
        p_teamA_wins_point = as_torch_tensor(p_teamA_wins_point, torch.float, device=self.device)
        if p_teamA_wins_deciding_point is not None:
            p_teamA_wins_deciding_point = as_torch_tensor(p_teamA_wins_deciding_point, torch.float, device=self.device)
        else:
            p_teamA_wins_deciding_point = p_teamA_wins_point

        # Checks
        assert p_teamA_wins_point.ndim == 1, "p_teamA_wins_point.shape must be (n_batches,)"
        if p_teamA_wins_deciding_point is not None:
            assert p_teamA_wins_deciding_point.ndim == 1, "p_teamA_wins_deciding_point.shape must be (n_batches,)"
        assert p_teamA_wins_point.shape == p_teamA_wins_deciding_point.shape, "p_teamA_wins_point.shape must be equal to p_teamA_wins_deciding_point.shape"
        
        # Compute probability of team A winning
        p_teamA_wins = \
            self.prob_teamA_wins_without_advantages(p_teamA_wins_point) + \
            self.prob_teamA_wins_during_advantages_before_deciding_point(p_teamA_wins_point) + \
            self.prob_teamA_wins_at_deciding_point(p_teamA_wins_point, p_teamA_wins_deciding_point)
    
        return p_teamA_wins
    
    
    def prob_teamA_wins_without_advantages (self, p_teamA_wins_point: Union[torch.Tensor, Sequence[float]]) -> torch.Tensor:
        """
        Compute the probability of team A winning without advantages

        Args:
            p_teamA_wins_point : torch.Tensor[torch.float] (n_batches,)
                Probability of team A winning a point.

        Returns:
            p_teamA_wins : torch.Tensor[torch.float] (n_batches,)
                Probability of team A winning without advantages.
        """

        # As torch tensor
        p_teamA_wins_point = as_torch_tensor(p_teamA_wins_point, torch.float, device=self.device)        

        # Checks
        assert p_teamA_wins_point.ndim == 1, "p_teamA_wins_point.shape must be (n_batches,)"

        # Compute probability of team A winning without advantages, summing over all possible scores
        score_teamA = torch.full_like(p_teamA_wins_point, fill_value=self.score_end, dtype=torch.long)
        p_teamA_wins_without_advantages = torch.zeros_like(p_teamA_wins_point, dtype=torch.float)
        for i_score in range(self.score_end-1):
            score_teamB = torch.full_like(p_teamA_wins_point, fill_value=i_score, dtype=torch.long)
            p_this_score = self.prob_this_score(score_teamA, score_teamB, p_teamA_wins_point)
            p_teamA_wins_without_advantages = p_teamA_wins_without_advantages + p_this_score

        return p_teamA_wins_without_advantages
        
    

    def prob_teamA_wins_during_advantages_before_deciding_point (self, p_teamA_wins_point: Union[torch.Tensor, Sequence[float]]) -> torch.Tensor:
        """
        Compute the probability of team A winning during advantages before deciding point

        Args:
            p_teamA_wins_point : torch.Tensor[torch.float] (n_batches,)
                Probability of team A winning a point.

        Returns:
            p_teamA_wins : torch.Tensor[torch.float] (n_batches,)
                Probability of team A winning during advantages before deciding point.
        """

        # As torch tensor
        p_teamA_wins_point = as_torch_tensor(p_teamA_wins_point, torch.float, device=self.device)
        
        # Checks
        if self.n_max_advantages == 0: return 0
        assert p_teamA_wins_point.ndim == 1, "p_teamA_wins_point.shape must be (n_batches,)"

        # Compute probability of team A winning during advantages before deciding point
        p = p_teamA_wins_point
        e1 = self.score_end-1
        g = 2*p*(1-p)
        if self.n_max_advantages is not None: 
            p_teamA_wins_during_advantages_before_deciding_point = \
                self._utils_binom[e1] * p**(e1+2) * (1-p)**e1 * (1-g**self.n_max_advantages) / (1-g)
        else: 
            p_teamA_wins_during_advantages_before_deciding_point = \
                self._utils_binom[e1] * p**(e1+2) * (1-p)**e1 / (1-g)
        
        return p_teamA_wins_during_advantages_before_deciding_point
    

    def prob_teamA_wins_at_deciding_point (
            self, 
            p_teamA_wins_point: Union[torch.Tensor, Sequence[float]], 
            p_teamA_wins_deciding_point: Optional[Union[torch.Tensor, Sequence[float]]] = None
        ) -> torch.Tensor:
        """
        Compute the probability of team A winning at deciding point

        Args:
            p_teamA_wins_point : torch.Tensor[torch.float] (n_batches,)
                Probability of team A winning a point.
            p_teamA_wins_deciding_point : torch.Tensor[torch.float] (n_batches,) = None
                Probability of team A winning the deciding point. Defaults to None, which implies using
                p_teamA_wins_point as p_teamA_wins_deciding_point
        
        Returns:
            p_teamA_wins : torch.Tensor[torch.float] (n_batches,)
                Probability of team A winning at deciding point.
        """

        # As torch tensor
        p_teamA_wins_point = as_torch_tensor(p_teamA_wins_point, torch.float, device=self.device)
        if p_teamA_wins_deciding_point is not None:
            p_teamA_wins_deciding_point = as_torch_tensor(p_teamA_wins_deciding_point, torch.float, device=self.device)
        else:
            p_teamA_wins_deciding_point = p_teamA_wins_point        
        
        # Checks
        if self.n_max_advantages is None: return 0
        assert p_teamA_wins_point.ndim == 1, "p_teamA_wins_point.shape must be (n_batches,)"
        assert p_teamA_wins_deciding_point.ndim == 1, "p_teamA_wins_deciding_point.shape must be (n_batches,)"
        assert p_teamA_wins_point.shape == p_teamA_wins_deciding_point.shape, "p_teamA_wins_point.shape must be equal to p_teamA_wins_deciding_point.shape"

        # Compute probability of team A winning at deciding point
        e1 = self.score_end-1
        p_teamA_wins_at_deciding_point = self._utils_binom[e1] * 2**self.n_max_advantages * \
            (p_teamA_wins_point*(1-p_teamA_wins_point))**(e1+self.n_max_advantages) * p_teamA_wins_deciding_point
        
        return p_teamA_wins_at_deciding_point
        

    def __repr__ (self):
        
        return f"BasiScoreBlock(score_end={self.score_end}, n_max_advantages={self.n_max_advantages})"
    

    def __str__ (self):
        
        return repr(self)
    

class ScoringSystem:
    """
    Abstract base class for scoring systems.

    Attributes:
        device : torch.device
            Device to store tensors on.
        n_score_elements : int
            Number of elements in the score. This should be defined in subclasses.

    Methods:
        process_score(score)
        prob_this_score(score, abilities)
        prob_teamA_wins(abilities)
    """


    def __init__ (self, device: torch.device = torch.device("cpu")) -> None:
        """
        A scoring system defines how to compute the probability of a given score.

        Args:
            device : torch.device
                Device to store tensors on. Defaults to CPU.
        """

        self.device = device
        self.n_score_elements = None  # This should be defined in subclasses


    def to (self, device: torch.device) -> None:
        """
        Move the internal tensors to a specified device.

        Args:
            device : torch.device
                Device to move the tensors to
        """

        if self.device != device:
            self.device = device

        raise NotImplementedError


    def process_score (self, score: list[int]) -> Tuple[bool, Union[list[int], None], str]:
        """
        Check if the score is valid, and get the normalized score and the winner team.

        Usage example:
            score = [6, 1, 6, 2]
            is_valid, normalized_score, winner_team = mrdodo.process_score(score)
            # is_valid = True
            # normalized_score = [6, 1, 6, 2, 0, 0]
            # winner_team = "Team A"

        Args:
            score : list[int] (n_elements,)
                The score to process.

        Returns:
            is_valid : bool
                True if the score is valid, False otherwise.
            normalized_score : list[int] (n_score_elements,)
                The normalized score if the score is valid, None otherwise. The normalized score is
                the score re-formatted to have n_score_elements elements, aligning it with the scoring
                system convetions. Typically, some dummy zeros can be added at the end.
            winner_team : str
                The team that won the match. "Team A" or "Team B", or None if is_valid is False.
        """

        raise NotImplementedError


    def prob_this_score (self, score: Union[torch.Tensor, Sequence[int]], abilities: Union[torch.Tensor, Sequence[float]]) -> torch.Tensor:
        """
        Compute the probability of a given score.

        Args:
            score: torch.Tensor[torch.long] (n_score_elements,) or (n_batches, n_score_elements)
                The score to compute the probability for.
            abilities : torch.Tensor[torch.float] (n_batches, 2) or (n_batches, 4)
                abilities of players. The last dimension must be in [2, 4]:
                    - 2: match type = single
                    - 4: match type = double

        Returns:
            p_this_score: torch.Tensor[torch.float] (n_batches,)
                The probability of the given score.
        """

        raise NotImplementedError


    def prob_teamA_wins (self, abilities: Union[torch.Tensor, Sequence[float]]) -> torch.Tensor:
        """
        Compute the probability of team A winning.

        Args:
            abilities : torch.Tensor[torch.float] (n_batches, 2) or (n_batches, 4)
                abilities of players. The last dimension must be in [2, 4]:
                    - 2: match type = single
                    - 4: match type = double

        Returns:
            p_teamA_wins: torch.Tensor[torch.float] (n_batches,)
                The probability of team A winning.
        """

        raise NotImplementedError


    def __repr__ (self):

        raise "Abstract ScoringSystem"


    def __str__ (self):

        return repr(self)
