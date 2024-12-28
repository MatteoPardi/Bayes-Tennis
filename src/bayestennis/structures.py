import pandas as pd
from typing import TypeAlias

TennisDataFrame: TypeAlias = pd.DataFrame
"""
A TennisDataFrame is a pandas DataFrame with the following columns:
    - id_match: Unique identifier for each match.
    - file_name: Name of the source file containing the match data.
    - file_path: Path to the source file containing the match data.
    - id_match_within_file: Unique identifier for the match within its source file.
    - is_valid: Flag indicating whether the match data is valid.
    - error_msg: Error message if the match data is not valid.
    - match_type: Type of match ('single' or 'double').
    - tournament: Name of the tournament.
    - scoring_system: Name of the scoring system.
    - date: Date of the match.
    - elapsed_days: Number of days elapsed since the match date (relative to now).
    - log_likelihood_weight: Weight associated with the match for log-likelihood computation.
    - id_teamA_player1: Unique identifier for player 1 in team A.
    - teamA_player1_name: Name of player 1 in team A.
    - id_teamA_player2: Unique identifier for player 2 in team A.
    - teamA_player2_name: Name of player 2 in team A.
    - id_teamB_player1: Unique identifier for player 1 in team B.
    - teamB_player1_name: Name of player 1 in team B.
    - id_teamB_player2: Unique identifier for player 2 in team B.
    - teamB_player2_name: Name of player 2 in team B.
    - score_AvsB_str: String representation of the score between team A and team B.
    - normalized_score_AvsB: Score of the match in the normalized format, ready to be processed.
    - winner_team: Name of the team that won the match ('team A' or 'team B').
"""

PlayersDataFrame: TypeAlias = pd.DataFrame
"""
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
"""

OptimizationInfo: TypeAlias = pd.DataFrame
"""
An OptimizationInfo is a pandas DataFrame with the following columns:
    - idx_iteration : iteration index
    - loss : loss value
"""
