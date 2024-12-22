from .. import scoring_systems
import pandas as pd
from typing import TypeAlias, Tuple
from glob import glob
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta

TennisDataFrame: TypeAlias = pd.DataFrame

# Load notion_tournaments_config as a pandas DataFrame
notion_tournaments_config = pd.read_csv(Path(__file__).resolve().parent / 'notion_tournaments_config.csv')
notion_tournaments_config.set_index('tournament', inplace=True)


def import_notion_csv (*file_paths: Tuple[str]) -> TennisDataFrame:
    """
    Import a TennisDataFrame from Notion CSV files.

    Args:
        *file_paths : Tuple[str]
            File paths to import. Notation with '*' is supported. E.g.:
                - 'path/to/file1.csv'
                - 'path/to/file*.csv'

    Returns:
        tdf : TennisDataFrame
            Tennis DataFrame containing the imported data.
    """

    # resolve file paths
    file_paths = resolve_file_paths(file_paths)

    # create a TennisDataFrame (tdf) for each file
    tdfs = []
    for file_path in file_paths:

        # Read CSV file as pandas DataFrame (df)
        df = pd.read_csv(file_path)
        assert len(df.columns) == 6, "Notion CSV file must have 6 columns: id, Teams, Players A, Players B, Score, Tournament"
        df.columns = ["id", "Teams", "Players A", "Players B", "Score", "Tournament"]

        # Parse DataFrame to TennisDataFrame, row-by-row
        tdf = df.apply(get_tdf_row_from_df_row, axis=1)
        tdf['id_match'] = None  # assigned later
        tdf['file_path'] = file_path
        tdf['file_name'] = str(Path(file_path).name)

        tdfs.append(tdf)

    # concatenate all TennisDataFrames
    tdf = pd.concat(tdfs, ignore_index=True)
    tdf['id_match'] = np.arange(len(tdf))

    # process tdf to assign the rest of the TennisDataFrame columns
    tdf = process_tdf(tdf)

    return tdf


def get_tdf_row_from_df_row (df_row: pd.Series) -> pd.Series:
    """
    Get a TennisDataFrame row from a DataFrame row.

    Args:
        df_row : pd.Series
            DataFrame row.

    Returns:
        tdf_row : pd.Series
            TennisDataFrame row.
    """

    # df_row columns:
    #   - 'id'
    #   - 'Teams'
    #   - 'Players A'
    #   - 'Players B'
    #   - 'Score'
    #   - 'Tournament'

    # Init an empty tdf_row
    tdf_row = pd.Series({
        'id_match': -1,  # assigned outside this function. See import_notion_csv()
        'file_name': "",  # assigned outside this function. See import_notion_csv()
        'file_path': "",  # assigned outside this function. See import_notion_csv()
        'id_match_within_file': -1,
        'is_valid': False,
        'error_msg': "",
        'match_type': "",
        'tournament': "",
        'scoring_system': "",
        'date': np.nan,
        'elapsed_days': np.nan,  # assigned outside this function. See process_tdf()
        'log_likelihood_weight': 0,  # assigned outside this function. See process_tdf()
        'id_teamA_player1': -1,  # assigned outside this function. See process_tdf()
        'teamA_player1_name': "",
        'id_teamA_player2': -1,  # assigned outside this function. See process_tdf()
        'teamA_player2_name': "",
        'id_teamB_player1': -1,  # assigned outside this function. See process_tdf()
        'teamB_player1_name': "",
        'id_teamB_player2': -1,  # assigned outside this function. See process_tdf()
        'teamB_player2_name': "",
        'score_AvsB_str': "",
        'normalized_score_AvsB': [],
        'winner_team': "",
    })

    # =============================================================================
    #   Process df_row id
    # =============================================================================

    tdf_row['id_match_within_file'] = df_row['id']

    # =============================================================================
    #   Process df_row players
    # =============================================================================

    # Get players team A
    try:
        players_teamA = df_row['Players A'].split(", ")        
    except Exception:
        tdf_row['is_valid'] = False
        tdf_row['error_msg'] = f"Players A not admittable: {df_row['Players A']}"
        return tdf_row

    # Get players team B
    try:
        players_teamB = df_row['Players B'].split(", ")        
    except Exception:
        tdf_row['is_valid'] = False
        tdf_row['error_msg'] = f"Players B not admittable: {df_row['Players B']}"
        return tdf_row
    
    # Check if both teams have the same number of players
    if len(players_teamA) != len(players_teamB) or len(players_teamA) not in [1, 2]:
        tdf_row['is_valid'] = False
        tdf_row['error_msg'] = f"Strange number of players. Is it a single or a double match?"
        return tdf_row
    
    # Assign match type
    if len(players_teamA) == 1:
        tdf_row['match_type'] = 'single'
        tdf_row['teamA_player1_name'] = players_teamA[0]
        tdf_row['teamA_player2_name'] = None
        tdf_row['teamB_player1_name'] = players_teamB[0]
        tdf_row['teamB_player2_name'] = None
    else:
        tdf_row['match_type'] = 'double'
        tdf_row['teamA_player1_name'] = players_teamA[0]
        tdf_row['teamA_player2_name'] = players_teamA[1]
        tdf_row['teamB_player1_name'] = players_teamB[0]
        tdf_row['teamB_player2_name'] = players_teamB[1]

    # Check if players name are admittable
    players = players_teamA + players_teamB
    is_admittable_player = [check_if_admittable_player(player) for player in players]
    if not all(is_admittable_player):
        tdf_row['is_valid'] = False
        players_not_admittable = [player for player, admittable in zip(players, is_admittable_player) if not admittable]
        tdf_row['error_msg'] = f"Players name not admittable: {players_not_admittable}"
        return tdf_row

    # =============================================================================
    #   Process df_row tournament
    # =============================================================================

    try:
        tournament_name = df_row['Tournament']
        tournament_info = notion_tournaments_config.loc[tournament_name]
    except Exception:
        tdf_row['is_valid'] = False
        tdf_row['error_msg'] = f"Tournament not recognized: {tournament_name}"
        return tdf_row

    tdf_row['tournament'] = tournament_name
    tdf_row['scoring_system'] = tournament_info['scoring_system']
    tdf_row['date'] = datetime.strptime(tournament_info['reference_date'], '%b %Y')

    # =============================================================================
    #   Process df_row score
    # =============================================================================

    tdf_row['score_AvsB_str'] = df_row['Score']

    # From score as string to score as list of int
    try:
        score_AvsB_as_list = get_score_as_list(tdf_row['score_AvsB_str'])
    except Exception:
        tdf_row['is_valid'] = False
        tdf_row['error_msg'] = f"Unable to understand score: {tdf_row['score_AvsB_str']}"
        return tdf_row
    
    # Get scoring system
    try:
        scoringSystemObj = getattr(scoring_systems, tdf_row['scoring_system'])()  # E.g.: MrDodo()
    except Exception:
        tdf_row['is_valid'] = False
        tdf_row['error_msg'] = f"Scoring system not recognized: {tdf_row['scoring_system']}"
        return tdf_row
    
    # Check if score is admittable and get normalized score and winner team
    try:
        is_admittable_score, normalized_score_AvsB, winner_team = scoringSystemObj.process_score(score_AvsB_as_list)
    except Exception:
        is_admittable_score = False
    if not is_admittable_score:
        tdf_row['is_valid'] = False
        tdf_row['error_msg'] = f"Score '{tdf_row['score_AvsB_str']}' is not admittable for the scoring system '{tdf_row['scoring_system']}'"
        return tdf_row

    tdf_row['normalized_score_AvsB'] = normalized_score_AvsB
    tdf_row['winner_team'] = winner_team

    # =============================================================================
    #   End
    # =============================================================================

    tdf_row['is_valid'] = True
    tdf_row['error_msg'] = ""

    return tdf_row


def resolve_file_paths (file_paths: Tuple[str]) -> list[str]:
    """
    Resolve file paths using glob.

    Args:
        file_paths : Tuple[str]
            File paths to resolve.

    Returns:
        resolved_file_paths : list[str]
            Resolved file paths.
    """

    resolved_file_paths = []
    for file_path in file_paths:
        resolved_file_paths += glob(file_path)

    return resolved_file_paths


def check_if_admittable_player (player: str) -> bool:
    """
    Check if player name is admittable.

    Args:
        player : str
            Player name.

    Returns:
        is_admittable : bool
            True if player name is admittable, False otherwise.
    """

    is_admittable = bool(player) and not player.casefold().startswith('boh')

    return is_admittable


def get_score_as_list (score: str) -> list[int]:
    """
    Get score as list of int

    Args:
        score : str
            Score as string. Examples:
                - "6-3 4-6 11-9"
                - "6-3 6-4"
    
    Returns:
        score_as_list : list[int]
            Score as list of int. Examples:
                - [6, 3, 4, 6, 11, 9]
                - [6, 3, 6, 4]
    """

    score_as_list = []
    for pair in score.split(' '):
        score_as_list += [int(n) for n in pair.split('-')]

    return score_as_list


def process_tdf (tdf: TennisDataFrame) -> TennisDataFrame:
    """
    Assign the value of remaining columns of the TennisDataFrame
    """

    # Filter out invalid rows
    tdf_valid = tdf[tdf['is_valid']]

    # Assign player IDs
    player_names = tdf_valid[['teamA_player1_name', 'teamA_player2_name', 'teamB_player1_name', 'teamB_player2_name']].stack().unique()
    player_ids = np.arange(len(player_names))
    name_to_id_dict = dict(zip(player_names, player_ids))
    name_to_id_map = lambda name: name_to_id_dict.get(name, -1)
    tdf['id_teamA_player1'] = tdf['teamA_player1_name'].map(name_to_id_map).astype(int)
    tdf['id_teamA_player2'] = tdf['teamA_player2_name'].map(name_to_id_map).astype(int)
    tdf['id_teamB_player1'] = tdf['teamB_player1_name'].map(name_to_id_map).astype(int)
    tdf['id_teamB_player2'] = tdf['teamB_player2_name'].map(name_to_id_map).astype(int)

    # Compute elapsed days
    current_date = datetime.now()
    tdf['elapsed_days'] = (current_date - tdf['date']) / timedelta(days=1)

    # Compute log likelihood weights
    half_life_days = 8 * 30  # 8 months. This hard-coded value can be adjusted later, if needed
    tdf['log_likelihood_weight'] = 2 ** (-tdf['elapsed_days'] / half_life_days)

    return tdf
