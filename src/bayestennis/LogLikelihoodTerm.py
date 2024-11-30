import torch
from .utils import as_torch_tensor, as_2dim_tensor


class LogLikelihoodTerm:
    """
    LogLikelihoodTerm represents a log-likelihood computation for a given scoring system.

    Attributes:
        scoring_system : ScoringSystem
            The scoring system used to compute probabilities.
        device : torch.device
            The device where tensors are stored.
        score_tensor : torch.Tensor (n_matches, n_score_elements)
            Stores scores for each match.
        player_indices_tensor : torch.Tensor (n_matches, 4)
            Stores player indices for each match. 4 players per match.
            Single matches are represented by
                [teamA_player1, teamA_player1, teamB_player1, teamB_player1]
            Double matches are represented by
                [teamA_player1, teamA_player2, teamB_player1, teamB_player2]
        weights_tensor : torch.Tensor (n_matches,)
            Weights for each match, used in log-likelihood computation.
        n_matches : int
            Number of matches stored.

    Methods:
        __call__(abilities_tensor)
        add(score, player_indices, weight)
        to(device)
    """


    def __init__ (self, scoring_system, device='cpu'):
        """
        Initialize the LogLikelihoodTerm with a scoring system and device.

        Args:
            scoring_system : ScoringSystem
                The scoring system to use for probability calculations.
            device : str or torch.device = 'cpu'
                The device to store tensors on.
        """

        self.scoring_system = scoring_system
        self.device = torch.device(device)
        self.score_tensor = torch.empty((0, self.scoring_system.n_score_elements), dtype=torch.long, device=self.device)
        self.player_indices_tensor = torch.empty((0, 4), dtype=torch.long, device=self.device)  # 4 players per match
        self.weights_tensor = torch.empty((0,), dtype=torch.float, device=self.device)
        self.n_matches = 0


    def __call__ (self, abilities_tensor):  
        """
        Compute the log-likelihood for a set of player abilities.

        Args:
            abilities_tensor : torch.Tensor (n_players,)
                A 1D tensor containing the abilities of each player.
                abilities_tensor[i] is the ability of the i-th player.

        Returns:
            log_likelihood_term : torch.Tensor (1,)
                The log-likelihood term. This is the sum of log-probabilities
                for each match weighted by the corresponding weight.
        """

        if self.n_matches == 0:
            return torch.tensor(0.0, device=self.device)
            
        # As torch tensor
        abilities_tensor = as_torch_tensor(abilities_tensor, torch.float).to(self.device)

        # Compute log-probabilities
        player_abilities = abilities_tensor[self.player_indices_tensor]
        probabilities = self.scoring_system.prob_this_score(self.score_tensor, player_abilities)
        log_probabilities = torch.log(probabilities + 1e-40)

        # Compute log-likelihood term
        log_likelihood_term = torch.sum(log_probabilities * self.weights_tensor)

        return log_likelihood_term


    def add (self, score, player_indices, weight):
        """
        Add new match data to the internal tensors.

        Args:
            score : torch.Tensor or array-like
                The scores for the new matches.
            player_indices : torch.Tensor or array-like
                The player indices for the new matches.
            weight : torch.Tensor or array-like
                The weights for the new matches.
        """

        # As torch tensors
        score = as_2dim_tensor(as_torch_tensor(score, torch_dtype=torch.long, device=self.device))
        player_indices = as_2dim_tensor(as_torch_tensor(player_indices, torch_dtype=torch.long, device=self.device))
        weight = as_torch_tensor(weight, torch_dtype=torch.float, device=self.device).reshape(-1)  # Reshape to 1D

        if score.shape[0] != player_indices.shape[0] or score.shape[0] != weight.shape[0]:
            raise ValueError("All inputs must have the same number of matches.")

        # Concatenate to internal tensors
        self.score_tensor = torch.cat([self.score_tensor, score], dim=0)
        self.player_indices_tensor = torch.cat([self.player_indices_tensor, player_indices], dim=0)
        self.weights_tensor = torch.cat([self.weights_tensor, weight], dim=0)
        self.n_matches = self.score_tensor.shape[0]


    def to (self, device):
        """
        Move tensors to the specified device.

        Args:
            device : torch.device
                The device to move tensors to.
        """

        if self.device != device:
            self.device = device
            self.score_tensor = self.score_tensor.to(device)
            self.player_indices_tensor = self.player_indices_tensor.to(device)
            self.weights_tensor = self.weights_tensor.to(device)


    def __repr__ (self):

        return f"{self.__class__.__name__}(scoring_system={self.scoring_system.__class__.__name__}, n_matches={self.n_matches})"


    def __str__ (self):

        return self.__repr__()
