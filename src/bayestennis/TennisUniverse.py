import pandas as pd
import numpy as np
import torch
from torch.optim.lr_scheduler import LambdaLR
from typing import TypeAlias, Union
from .Loss import Loss
from .utils import TicToc

TennisDataFrame: TypeAlias = pd.DataFrame
PlayersDataFrame: TypeAlias = pd.DataFrame
OptimizationInfo: TypeAlias = pd.DataFrame


class TennisUniverse:
    """
    TennisUniverse is the main class of the package, to manage a TennisDataFrame and perform optimization.

    Attributes:
        tennisDataFrame : TennisDataFrame
            The TennisDataFrame containing the data.
        playersDataFrame : PlayersDataFrame
            The PlayersDataFrame containing the player information.
        loss : Loss
            The Loss object used for optimization.
        device : torch.device
            The device to store tensors on.        

    Methods:
        get_playersDataFrame_from_tennisDataFrame(tennisDataFrame)
        get_loss_from_tennisDataFrame(tennisDataFrame)
        optimize(TBD)

    Structure description:
        TennisDataFrame
            Please see structures.py.
        PlayersDataFrame
            A PlayersDataFrame is a pandas DataFrame with the following columns:
            - id_player : unique player identifier
            - name : player name
            - ability : player ability
            - rank : player rank
            - n_singles : number of singles matches
            - n_doubles : number of doubles matches
            - n_matches : total number of matches
            - last_date : last match date played
            - last_tournament : last tournament player played
        OptimizationInfo
            An OptimizationInfo is a pandas DataFrame with the following columns:
            - idx_iteration : iteration index
            - loss : loss value 
    """

    def __init__ (self, tennisDataFrame: TennisDataFrame, device: Union[str, torch.device] = 'cpu') -> None:
        """
        Initialize the TennisUniverse with a TennisDataFrame and a device.

        Args:
            tennisDataFrame : TennisDataFrame
                The TennisDataFrame containing the data.
            device : str or torch.device = 'cpu'
                The device to store tensors on.
        """

        self.device = torch.device(device)
        self.tennisDataFrame = tennisDataFrame
        self.playersDataFrame = self.get_playersDataFrame_from_tennisDataFrame(self.tennisDataFrame)
        self.loss = self.get_loss_from_tennisDataFrame(self.tennisDataFrame)

        self.loss.to(self.device)


    def get_playersDataFrame_from_tennisDataFrame(self, tdf: TennisDataFrame) -> PlayersDataFrame:
        """
        Create a PlayersDataFrame from a TennisDataFrame.

        Args:
            tdf : TennisDataFrame
                The TennisDataFrame containing the data.

        Returns:
            playersDataFrame : PlayersDataFrame
                The PlayersDataFrame containing the player information.
        """

        # Filter out invalid rows
        tdf_valid = tdf[tdf['is_valid']]

        # Extract all player-related information
        player_records = []
        for _, row in tdf_valid.iterrows():
            if row['match_type'] == 'single':
                player_records.append({'id_player': row['id_teamA_player1'], 'name': row['teamA_player1_name'], 'match_type': 'single', 'date': row['date'], 'tournament': row['tournament']})
                player_records.append({'id_player': row['id_teamB_player1'], 'name': row['teamB_player1_name'], 'match_type': 'single', 'date': row['date'], 'tournament': row['tournament']})
            elif row['match_type'] == 'double':
                player_records.append({'id_player': row['id_teamA_player1'], 'name': row['teamA_player1_name'], 'match_type': 'double', 'date': row['date'], 'tournament': row['tournament']})
                player_records.append({'id_player': row['id_teamA_player2'], 'name': row['teamA_player2_name'], 'match_type': 'double', 'date': row['date'], 'tournament': row['tournament']})
                player_records.append({'id_player': row['id_teamB_player1'], 'name': row['teamB_player1_name'], 'match_type': 'double', 'date': row['date'], 'tournament': row['tournament']})
                player_records.append({'id_player': row['id_teamB_player2'], 'name': row['teamB_player2_name'], 'match_type': 'double', 'date': row['date'], 'tournament': row['tournament']})
        player_records = pd.DataFrame(player_records)

        # Group by player id to compute required statistics
        grouped = player_records.groupby('id_player')

        playersDataFrame = grouped.apply(lambda group: pd.Series({
            'name': group['name'].iloc[0],
            'ability': np.nan,
            'rank': np.nan,
            'n_singles': (group['match_type'] == 'single').sum(),
            'n_doubles': (group['match_type'] == 'double').sum(),
            'n_matches': len(group),
            'last_date': group['date'].max(),
            'last_tournament': group.loc[group['date'].idxmax(), 'tournament']
        })).reset_index()

        return playersDataFrame
    

    def get_loss_from_tennisDataFrame (self, tdf: TennisDataFrame) -> Loss:
        """
        Create a Loss function object from a TennisDataFrame.

        Args:
            tdf : TennisDataFrame
                The TennisDataFrame containing the data.

        Returns:
            loss : Loss
                The Loss function object used for optimization.
        """

        # Filter out invalid rows
        tdf_valid = tdf[tdf['is_valid']]

        # Init loss
        loss = Loss()

        # Add log likelihood terms
        for _, row in tdf_valid.iterrows():

            scoring_system_name = row['scoring_system']
            score = row['normalized_score_AvsB']
            weight = row['log_likelihood_weight']

            if row['match_type'] == 'single':
                player_indices = [row['id_teamA_player1'], row['id_teamA_player1'], row['id_teamB_player1'], row['id_teamB_player1']]
            elif row['match_type'] == 'double':
                player_indices = [row['id_teamA_player1'], row['id_teamA_player2'], row['id_teamB_player1'], row['id_teamB_player2']]
            else:
                raise ValueError(f"Invalid match type: {row['match_type']}")

            loss.add(scoring_system_name, score, player_indices, weight)
            
        return loss


    def optimize (self, 
                  n_iter: int = 1000, 
                  lr_start: float = 1e-1,
                  lr_end: float = 1e-3,
                  verbose: int = 100) -> OptimizationInfo:
        """
        Optimize player abilities by minimizing the loss function.

        Description:
            This method optimizes the player abilities stored in the `playersDataFrame`
            by minimizing the loss function. It uses an Adam optimizer and an exponential
            learning rate schedule.

        Args:
            n_iter : int = 1000
                Number of optimization iterations.
            lr_start : float = 0.1
                Initial learning rate.
            lr_end : float = 0.001
                Final learning rate.
            verbose : int = 100
                Frequency of logging the progress. Set to 0 for no logging.

        Returns:
            optimization_info : OptimizationInfo
                DataFrame containing iteration indices and corresponding loss values.
        """

        # DEBUG
        #torch.autograd.set_detect_anomaly(True)
        # DEBUG

        # Ensure CUDA availability if specified
        if self.device.type == 'cuda' and not torch.cuda.is_available():
            raise Exception("Unable to use CUDA: CUDA is not available")

        # Initialize abilities tensor on the specified device
        n_players = len(self.playersDataFrame)
        abilities_tensor = torch.zeros(n_players, device=self.device, dtype=torch.float, requires_grad=True)

        # Configure optimizer and learning rate scheduler
        optimizer = torch.optim.Adam([abilities_tensor], lr=lr_start)
        lr_policy = LR_Exponential_Policy(lr_start, lr_end, n_iter)
        scheduler = LambdaLR(optimizer, lr_lambda=lr_policy)

        # Initialize container for optimization logs
        optimization_info = {
            "idx_iteration": [],
            "loss": [],
        }

        # Timer for verbose output
        timer = TicToc()

        # Begin optimization loop
        if verbose:
            timer.tic()
            print("Optimization started:")

        for i_iter in range(n_iter):
            # Compute loss and gradients
            loss = self.loss(abilities_tensor)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            scheduler.step()

            # Log progress if verbose
            if verbose and i_iter % verbose == 0:
                print(f"  {i_iter} / {n_iter}: Loss = {loss.item():.6f}")

            # Record iteration data
            optimization_info["idx_iteration"].append(i_iter)
            optimization_info["loss"].append(loss.item())

        # Final verbose output
        if verbose:
            print(f"  {n_iter} / {n_iter}: Loss = {loss.item():.6f} (end)")
            timer.toc()

        # Post-process abilities
        abilities_tensor.requires_grad_(False)
        abilities_numpy = abilities_tensor.cpu().numpy()

        # Normalize abilities so median is 100
        abilities_numpy = abilities_numpy + 100 - np.quantile(abilities_numpy, 0.5)

        # Assign abilities to playersDataFrame and compute rank
        self.playersDataFrame['ability'] = self.playersDataFrame['id_player'].map(
            lambda id_player: abilities_numpy[id_player]
        )
        self.playersDataFrame['rank'] = self.playersDataFrame['ability'].rank(ascending=False)

        # Convert optimization logs to DataFrame
        optimization_info_df = pd.DataFrame(optimization_info)

        return optimization_info_df
    

    def __repr__ (self):

        n_players = len(self.playersDataFrame)
        n_matches = len(self.tennisDataFrame[self.tennisDataFrame['is_valid']])
        return f"TennisUniverse(n_players={n_players}, n_matches={n_matches})"
    

    def __str__ (self):

        return repr(self)        


class LR_Exponential_Policy:
    """
    A class to implement an exponential learning rate policy.
    
    Attributes:
        ratio : float
            The ratio between the final and initial learning rates.
        tau : int
            The number of iterations minus one.
        base : float
            The base for exponential calculation, calculated when tau is not zero.
    """
    
    def __init__(self, lr_start, lr_end, n_iter):
        """
        Initialize the exponential policy with start and end learning rates, and number of iterations.
        
        Args:
            lr_start : float
                The initial learning rate.
            lr_end : float
                The final learning rate.
            n_iter : int
                The number of iterations over which to apply the policy.
        """

        self.ratio = lr_end / lr_start
        self.tau = n_iter - 1
        if self.tau:
            self.base = self.ratio ** (1 / self.tau)

    def __call__(self, n):
        """
        Calculate the learning rate for a given iteration.
        
        Args:
            n : int
                The current iteration number.
        
        Returns:
            lr: float
                The learning rate for iteration n.
        """

        if n < self.tau:
            return self.base ** n
        else:
            return self.ratio
