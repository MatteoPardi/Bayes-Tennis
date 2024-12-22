import pandas as pd
from typing import TypeAlias

TennisDataFrame: TypeAlias = pd.DataFrame


def init_TennisDataFrame () -> TennisDataFrame:
    """
    This function returns an empty TennisDataFrame.

    Usage example:
        tdf = init_TennisDataFrame()
    
    Description:
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
    
    Args:
        None

    Returns:
        tdf : pd.DataFrame
            An empty TennisDataFrame
    """

    columns = [
        'id_match',
        'file_name',
        'file_path',
        'id_match_within_file',
        'is_valid',
        'error_msg',
        'match_type',
        'tournament',
        'scoring_system',
        'date',
        'elapsed_days',
        'log_likelihood_weight',
        'id_teamA_player1',
        'teamA_player1_name',
        'id_teamA_player2',
        'teamA_player2_name',
        'id_teamB_player1',
        'teamB_player1_name',
        'id_teamB_player2',
        'teamB_player2_name',
        'score_AvsB_str',
        'normalized_score_AvsB',
        'winner_team'
    ]

    # Create an empty TennisDataFrame
    tdf = pd.DataFrame(columns=columns)

    return tdf
