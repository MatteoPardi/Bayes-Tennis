import torch
from .LogLikelihoodTerm import LogLikelihoodTerm
from .utils import as_torch_tensor
from . import scoring_systems
from math import pi
from typing import Union, Sequence


class Loss:
    """
    Loss function class

    Attributes:
        device : torch.device
            Device to store tensors on.
        logLikelihoodTerms : dict[str, LogLikelihoodTerm]
            Dictionary to store log-likelihood terms.
        regularizationTerm : callable
            Regularization term to be applied.

    Methods:
        __call__(abilities_tensor)
        to(device)
        add(scoring_system_name, score, player_indices, weight)
    """

    def __init__ (self, Regularization: str = 'L2', coupling_const: float = 1/(2*pi), device: Union[str, torch.device] = 'cpu') -> None:
        """
        Initialize the Loss class with regularization and device.

        Args:
            Regularization : str = 'L2'
                Type of regularization ('L1' or 'L2').
            coupling_const : float = 1/(2*pi)
                Coupling constant for regularization.
            device : str or torch.device = 'cpu'
                Device to store tensors on.
        """

        self.device = torch.device(device)
        
        self.logLikelihoodTerms: dict[str, LogLikelihoodTerm] = {}

        if Regularization == 'L1':
            self.regularizationTerm = L1_Regularization(coupling_const, device=self.device)
        elif Regularization == 'L2':
            self.regularizationTerm = L2_Regularization(coupling_const, device=self.device)
        else:
            raise ValueError("Regularization must be 'L1' or 'L2'")


    def __call__ (self, abilities_tensor: torch.Tensor) -> torch.Tensor:
        """
        Calculate the total loss summing (negative) log-likelihood and regularization.

        Args:
            abilities_tensor : torch.Tensor (n_players,)
                A 1D tensor containing the abilities of each player.
                abilities_tensor[i] is the ability of the i-th player.

        Returns:
            loss : torch.Tensor (scalar)
                Total loss value.
        """

        # Init loss
        loss = torch.tensor(0., dtype=torch.float, device=self.device)

        # Sum (negative) log-likelihood terms
        for _, logLikelihoodTerm in self.logLikelihoodTerms.items():
            loss = loss - logLikelihoodTerm(abilities_tensor)

        # Add regularization term  
        loss = loss + self.regularizationTerm(abilities_tensor)

        return loss


    def to (self, device: torch.device) -> None:
        """
        Move tensors to the specified device.

        Args:
            device : torch.device
                Device to move tensors to.
        """

        if self.device != device:
            self.device = device
            for _, logLikelihoodTerm in self.logLikelihoodTerms.items():
                logLikelihoodTerm.to(device)
            self.regularizationTerm.to(device)

    
    def add (self, scoring_system_name: str, score: Union[torch.Tensor, Sequence], player_indices: Union[torch.Tensor, Sequence], weight: Union[torch.Tensor, Sequence]) -> None:
        """
        Add new match data to the log-likelihood term specified by scoring_system_name.

        Args:
            scoring_system_name : str
                Name of the scoring system to add data to.
            score : torch.Tensor or array-like (n_matches, n_score_elements) or (n_score_elements,)
                Scores for the new matches.
            player_indices : torch.Tensor or array-like (n_matches, 4) or (4,)
                Player indices for the new matches.
            weight : torch.Tensor or array-like (n_matches,) or scalar
                Weights for the new matches.
        """

        # Init the log-likelihood term if it does not already exist in self.logLikelihoodTerms
        if scoring_system_name not in self.logLikelihoodTerms:
            ScoringSystemClass = getattr(scoring_systems, scoring_system_name)
            self.logLikelihoodTerms[scoring_system_name] = LogLikelihoodTerm(ScoringSystemClass(), device=self.device)

        # Add new match data to the log-likelihood term
        self.logLikelihoodTerms[scoring_system_name].add(score, player_indices, weight)

    
    def __repr__ (self):
        
        lsit_of_str = [f"Loss Function. Terms:"]
        for scoring_system_name, logLikelihoodTerm in self.logLikelihoodTerms.items():
            lsit_of_str.append(f"  {scoring_system_name}: {logLikelihoodTerm}")
        lsit_of_str.append(f"  Regularization: {self.regularizationTerm}")

        return "\n".join(lsit_of_str)


    def __str__ (self):
        
        return self.__repr__()


class L1_Regularization:
    """
    L1 Regularization class.

    Attributes:
        coupling_const : float
            Coupling constant for regularization.
        device : torch.device
            Device to store tensors on.

    Methods:
        __call__(abilities_tensor)
        to(device)
    """

    def __init__ (self, coupling_const: float, device: Union[str, torch.device] = 'cpu') -> None:
        """
        Initialize L1 regularization with coupling constant and device.

        Args:
            coupling_const : float
                Coupling constant for regularization.
            device : str or torch.device
                Device to store tensors on.
        """

        if coupling_const <= 0:
            raise ValueError("coupling_const must be greater than 0")

        self.coupling_const = coupling_const
        self.device = torch.device(device)


    def __call__ (self, abilities_tensor: torch.Tensor) -> torch.Tensor:
        """
        Compute the L1 regularization term.

        Args:
            abilities_tensor : torch.Tensor (n_players,)
                A 1D tensor containing the abilities of each player.
                abilities_tensor[i] is the ability of the i-th player.

        Returns:
            regularization_term : torch.Tensor (scalar)
                L1 regularization term.
        """
        # As torch tensor
        abilities_tensor = as_torch_tensor(abilities_tensor, torch_dtype=torch.float, device=self.device)
        assert abilities_tensor.ndim == 1, "abilities_tensor.shape must be (n_players,)"

        # Compute regularization term
        regularization_term = self.coupling_const * torch.sum(abilities_tensor.abs())

        return regularization_term

    def to (self, device: torch.device) -> None:
        """
        Move tensors to the specified device.

        Args:
            device : torch.device
                Device to move tensors to.
        """
        
        self.device = device


    def __repr__ (self):
        
        return f"L1_Regularization(coupling_const={self.coupling_const})"


    def __str__ (self):
        
        return self.__repr__()


class L2_Regularization:
    """
    L2 Regularization class.

    Attributes:
        coupling_const : float
            Coupling constant for regularization.
        device : torch.device
            Device to store tensors on.

    Methods:
        __call__(abilities_tensor)
        to(device)
    """

    def __init__ (self, coupling_const: float, device: Union[str, torch.device] = 'cpu') -> None:
        """
        Initialize L2 regularization with coupling constant and device.

        Args:
            coupling_const : float
                Coupling constant for regularization.
            device : str or torch.device
                Device to store tensors on.
        """

        if coupling_const <= 0:
            raise ValueError("coupling_const must be greater than 0")
        self.coupling_const = coupling_const
        self.device = torch.device(device)


    def __call__ (self, abilities_tensor: torch.Tensor) -> torch.Tensor:
        """
        Compute the L2 regularization term.

        Args:
            abilities_tensor : torch.Tensor (n_players,)
                A 1D tensor containing the abilities of each player.
                abilities_tensor[i] is the ability of the i-th player.

        Returns:
            regularization_term : torch.Tensor (scalar)
                L2 regularization term.
        """

        # As torch tensor
        abilities_tensor = as_torch_tensor(abilities_tensor, torch_dtype=torch.float, device=self.device)
        assert abilities_tensor.ndim == 1, "abilities_tensor.shape must be (n_players,)"

        # Compute regularization term
        regularization_term = self.coupling_const * torch.sum(abilities_tensor**2) 

        return regularization_term


    def to (self, device: torch.device) -> None:
        """
        Move tensors to the specified device.

        Args:
            device : torch.device
                Device to move tensors to.
        """

        self.device = device


    def __repr__ (self):
        
        return f"L2_Regularization(coupling_const={self.coupling_const})"


    def __str__ (self):
        
        return self.__repr__()
