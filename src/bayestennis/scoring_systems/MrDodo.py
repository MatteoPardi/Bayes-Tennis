from typing import Sequence, Union
import torch
from .base import BasicScoreBlock, prob_teamA_wins_point, ScoringSystem
from ..utils import as_torch_tensor, as_2dim_tensor


class MrDodo (ScoringSystem):
    """
    MrDodo scoring system.

    Attributes:
        device : torch.device
            Device to store tensors on.
        n_score_elements : int
            Number of elements in a score.
        game : BasicScoreBlock(score_end=4, n_max_advantages=1)
            Game score block.
        set_tie_break : BasicScoreBlock(score_end=7)
            Set tie break score block.
        set : BasicScoreBlock(score_end=6, n_max_advantages=1)
            Set score block.
        match_tie_break : BasicScoreBlock(score_end=10)
            Match tie break score block.
        match : BasicScoreBlock(score_end=2, n_max_advantages=0)
            Match score block.

    Methods:
        to(device)
        check_score(score)
        prob_this_score(score, abilities)
        prob_teamA_wins(abilities)
    """


    def __init__ (self, device: torch.device = torch.device("cpu")) -> None:
        """
        MrDodo scoring system.

        Args:
            device : torch.device = torch.device("cpu")
                Device to store tensors on. Defaults to CPU.
        """

        self.device = device
        self.n_score_elements = 6
        self.game = BasicScoreBlock(score_end=4, n_max_advantages=1, device=device)
        self.set_tie_break = BasicScoreBlock(score_end=7, device=device)
        self.set = BasicScoreBlock(score_end=6, n_max_advantages=1, device=device)
        self.match_tie_break = BasicScoreBlock(score_end=10, device=device)
        self.match = BasicScoreBlock(score_end=2, n_max_advantages=0, device=device)


    def to (self, device: torch.device) -> None:
        """
        Move the internal tensors to a specified device.

        Args:
            device : torch.device
                Device to move the tensors to
        """

        if self.device != device:
            self.device = device
            self.game.to(device)
            self.set_tie_break.to(device)
            self.set.to(device)
            self.match_tie_break.to(device)
            self.match.to(device)

    
    def check_score (self, score: list[int]):
        """
        Check if the score is valid.

        Usage example:
            mrdodo = MrDodo()
            score = [6, 1, 6, 2]
            is_valid, normalized_score = mrdodo.check_score(score)
            score = [6, 1, 6, 2, 0, 0]
            is_valid, normalized_score = mrdodo.check_score(score)
            score = [6, 3, 6, 7, 10, 6]
            is_valid, normalized_score = mrdodo.check_score(score)

        Args:
            score : list[int] (n_elements,)
                The score to check. n_elements must be 4 (no match tie-break) or 6 (with match tie-break).
                The score elements represent the number of games won within each set.
                The order of the elements is:
                    [set1_teamA, set1_teamB, set2_teamA, set2_teamB, match_tiebreak_teamA, match_tiebreak_teamB].

        Returns:
            is_valid : bool (1,)
                True if the score is valid, False otherwise.
            normalized_score : list[int] (n_score_elements,)
                A list of 6 integers representing the normalized score, or None if is_valid is False.
                The score is always normalized to 6 elements in the format:
                    [set1_teamA, set1_teamB, set2_teamA, set2_teamB, match_tiebreak_teamA, match_tiebreak_teamB].
                If the input score had 4 elements (no match tiebreak), [0, 0] is appended.
        """

        # Preprocess: add [0, 0] for match tie-break if not present
        if len(score) == 4: score += [0,0]
        if len(score) != 6: return False

        # Get result strings
        set_1_result_str = self._get_result_str_from_score_set(score[0], score[1])
        if set_1_result_str is None:
            return False, None
        set_2_result_str = self._get_result_str_from_score_set(score[2], score[3])
        if set_2_result_str is None:
            return False, None
        match_tie_break_result_str = self._get_result_str_from_score_match_tie_break(score[4], score[5])
        if match_tie_break_result_str is None:
            return False, None
        
        # Determine if the score is valid and return the score
        list_result_str = [set_1_result_str, set_2_result_str, match_tie_break_result_str]   
        if list_result_str == ['A win', 'A win', 'no tie break']: return True, score
        if list_result_str == ['B win', 'B win', 'no tie break']: return True, score
        if list_result_str == ['A win', 'B win', 'A win']: return True, score
        if list_result_str == ['A win', 'B win', 'B win']: return True, score
        if list_result_str == ['B win', 'A win', 'A win']: return True, score
        if list_result_str == ['B win', 'A win', 'B win']: return True, score
        return False, None


    def prob_this_score (self, score: Union[torch.Tensor, Sequence[int]], abilities: Union[torch.Tensor, Sequence[float]]) -> torch.Tensor:
        """
        Compute the probability of a given score.

        Args:
            score: torch.Tensor[torch.long] (n_batches, n_score_elements)
                The score to compute the probability for.
                n_score_elements must be 6. See check_score method for details.
            abilities : torch.Tensor[torch.float] (n_batches, 2) or (n_batches, 4)
                abilities of players. The last dimension must be in [2, 4]:
                    - 2: match type = single
                    - 4: match type = double

        Returns:
            p_this_score: torch.Tensor[torch.float] (n_batches,)
                The probability of the given score.
        """

        # As 2D torch tensors
        score = as_2dim_tensor(as_torch_tensor(score, torch.long, device=self.device))
        abilities = as_2dim_tensor(as_torch_tensor(abilities, torch.float, device=self.device))

        # Checks
        if score.shape[-1] != self.n_score_elements:
            raise Exception(f"score.shape[-1] must be {self.n_score_elements}")

        # Compute utility probabilities
        p_teamA_wins_point = prob_teamA_wins_point(abilities)
        p_teamA_wins_game = self.game.prob_teamA_wins(p_teamA_wins_point)
        p_teamA_wins_set_tie_break = self.set_tie_break.prob_teamA_wins(p_teamA_wins_point)

        # Compute probability of this score
        p_this_score = \
            self.set.prob_this_score(score[:, 0], score[:, 1], p_teamA_wins_game, p_teamA_wins_set_tie_break) * \
            self.set.prob_this_score(score[:, 2], score[:, 3], p_teamA_wins_game, p_teamA_wins_set_tie_break) * \
            self.match_tie_break.prob_this_score(score[:, 4], score[:, 5], p_teamA_wins_point)

        return p_this_score


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

        # As 2D torch tensors
        abilities = as_2dim_tensor(as_torch_tensor(abilities, torch.float, device=self.device))

        # Compute utility probabilities
        p_teamA_wins_point = prob_teamA_wins_point(abilities)
        p_teamA_wins_game = self.game.prob_teamA_wins(p_teamA_wins_point)
        p_teamA_wins_set_tie_break = self.set_tie_break.prob_teamA_wins(p_teamA_wins_point)
        p_teamA_wins_set = self.set.prob_teamA_wins(p_teamA_wins_game, p_teamA_wins_set_tie_break)
        p_teamA_wins_match_tie_break = self.match_tie_break.prob_teamA_wins(p_teamA_wins_point)

        # Compute probability of team A winning the match
        p_teamA_wins = self.match.prob_teamA_wins(p_teamA_wins_set, p_teamA_wins_match_tie_break)

        return p_teamA_wins
    

    def _get_result_str_from_score_set (self, a: int, b: int) -> Union[str, None]:
        """
        Determine the result string from a given score set.

        Args:
            a : int
                Score of team A.
            b : int
                Score of team B.

        Returns:
            str | None
                The result string ('A win' or 'B win') if the score is valid, None otherwise.
        """

        _max = max(a, b)
        _min = min(a, b)
        if _min < 0: return None
        if _max not in [6, 7]: return None
        if _max == 6 and _min > 4: return None
        if _max == 7 and _min not in [5, 6]: return None
        if a > b: return 'A win'
        else: return 'B win'
    
    
    def _get_result_str_from_score_match_tie_break (self, a: int, b: int) -> Union[str, None]:
        """
        Determine the result string from a given score match tie-break.

        Args:
            a : int
                Score of team A.
            b : int
                Score of team B.

        Returns:
            str | None
                The result string ('A win' or 'B win' or 'no tie break') if the score is valid, None otherwise.
        """

        if a == 0 and b == 0: return 'no tie break'
        _max = max(a, b)
        _min = min(a, b)
        if _min < 0: return None
        if _max < 10: return None
        if _max == 10 and _min > 8: return None
        if _max > 10 and _min != _max-2: return None
        if a > b: return 'A win'
        else: return 'B win'     


    def __repr__(self):

        list_of_str = [
            f"{self.__class__.__name__} scoring system:",
            f"  n_score_elements: {self.n_score_elements}",
            f"  Game: {repr(self.game)}",
            f"  TieBreak(Set): {repr(self.set_tie_break)}",
            f"  Set: {repr(self.set)}",
            f"  TieBreak(Match): {repr(self.match_tie_break)}",
            f"  Match: {repr(self.match)}"
        ]

        repr_str = "\n".join(list_of_str)
        return repr_str
