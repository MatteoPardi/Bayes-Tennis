import os
from glob import glob
import pandas as pd
import torch as th
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ._loss import Loss
from . import scoring_systems


# -------------------------------------------------------------------------------------
#    TennisUniverse_Base
# -------------------------------------------------------------------------------------


class TennisUniverse_Base:
    
    def __init__ (self, *paths):
        
        self.files = self._get_files(paths)
        self.df = self._df_from_files()
        self.players = { # ~~> pd.DataFrame(index='player_idx')
            'player_idx': [], 
            'player': []
        }
        self.n_players = 0
        self.abilities = th.tensor([], dtype=th.float)
        self.ranking = { # ~~> pd.DataFrame(index='rank') 
            'rank': [],
            'player': [],
            'ability': [],
            'n_singles': [],
            'n_doubles': [],
            'n_tot': [],
            'last_tournament': [],
            'last_tournament_date': []
        }
        self.loss = Loss()
        self.rejected = { # ~~> pd.DataFrame(index=['file','file_row'])
            'file': [],
            'file_row': [],
            'error_type': []
        }
        self.tournaments = []
        self.init_date = datetime.now()
        self._build_universe_from_df() # here: dict ~~> pd.DataFrame
        
    def save (self, path):
    
        if path.endswith('.csv'): self.ranking.to_csv(path)
        elif path.endswith('.xlsx'): self.ranking.to_excel(path)
        else: self.ranking.to_csv(path+'.csv')
        
    def _get_files (self, paths):
        
        files = []
        for path in paths: files += glob(path)
        return files
    
    def _df_from_files (self):
        
        df_list = []
        for file in self.files:
            df_list.append(self._df_from_file(file))
        return pd.concat(df_list, ignore_index=False)
    
    def _df_from_file (self, file):
        
        df = pd.DataFrame()
        file_df = pd.read_csv(file)
        for key in ['players A', 'players B', 'score', 'tournament']:
            df[key] = file_df[self._how_it_is_called_in_this_file(key, file_df.columns)]  
        df['file'] = file
        df['file_row'] = pd.Series(list(range(len(df))))
        df.set_index(['file', 'file_row'], inplace=True)
        return df
            
    def _how_it_is_called_in_this_file (self, key, file_columns):
        
        try: k = [_key for _key in file_columns if _key.casefold() in _accepted_keys[key]][0]
        except IndexError: 
            raise Exception("Unable to find a compatible key for '" + key + "' in file_columns")
        return k
    
    def _build_universe_from_df (self):
        
        self._players = {}
        for _, row in self.df.iterrows():
            self._load_row(row)
        self._players__from_dict_to_df()
        self._init_abilities_to_100()
        self._ranking__from_dict_to_df()
        self._rejected__from_dict_to_df()
            
    def _load_row (self, row):
        
        # -------- tournament step --------
        try: tournament_info = _tournaments_config.loc[row['tournament']]
        except KeyError: 
            self._reject(row, "tournament not recognized")
            return           
        scoring_system = tournament_info['scoring_system']
        date = tournament_info['date']
        passed_months = self._compute_passed_months(date)
        
        # -------- score step --------        
        try: score = self._get_score_as_list(row['score'])
        except ValueError: 
            self._reject(row, "score not admittable")
            return
        score = scoring_systems.check_if_admittable_score[scoring_system](score)
        if not score:
            self._reject(row, "score not admittable")
            return
        
        # -------- players step --------
        try:
            players_A = row['players A'].split(", ")        
            players_B = row['players B'].split(", ")
        except AttributeError: # if row['players A'] is not a string...
            self._reject(row, "players not admittable")
            return 
        if len(players_A) != len(players_B) or len(players_A) not in [1,2]: 
            self._reject(row, "strange number of players")
            return 
        players = players_A + players_B
        players_are_admittable = self._check_if_admittable_players(players)
        if not players_are_admittable:
            self._reject(row, "players not admittable")
            return
        match_type = 'singles' if len(players_A) == 1 else 'doubles'
        
        # -------- add step --------
        self._add_tournament_if_new(tournament_info.name)
        self._add_players_if_new(players)
        self._update_players_n_singles_n_doubles(players, match_type)
        self._update_players_last_tournament(players, row['tournament'], date)
        players_idx = [self._players[player]['idx'] for player in players]
        if match_type == 'singles': players_idx = [players_idx[0]]*2 + [players_idx[1]]*2 # as a doubles
        self.loss.add(scoring_system, score, players_idx, passed_months)        
            
    def _reject (self, row, error_type):
        
        self.rejected['file'].append(row.name[0])
        self.rejected['file_row'].append(row.name[1])
        self.rejected['error_type'].append(error_type)
        
    def _compute_passed_months (self, date):
        
        date = datetime.strptime(date, '%b %Y')
        diff = relativedelta(self.init_date, date)
        return diff.years*12 + diff.months
    
    def _get_score_as_list (self, score):
        
        score_as_list = []
        for pair in score.split(' '): score_as_list += [int(n) for n in pair.split('-')]
        return score_as_list
    
    def _check_if_admittable_players (self, players):
        
        return not any(player.casefold().startswith('boh') or not bool(player) for player in players)
        
    def _add_tournament_if_new (self, tournament):
        
        if tournament not in self.tournaments: self.tournaments.append(tournament)
    
    def _add_players_if_new (self, players):
        
        for player in players:
            if player not in self._players: 
                self._players[player] = {'idx': self.n_players, 'n_singles': 0, 'n_doubles': 0, \
                                         'last_tournament': None, 'last_tournament_date': None, \
                                         'last_tournament_dateTime': None}
                self.n_players += 1   
                
    def _update_players_n_singles_n_doubles (self, players, match_type):
        
        n_what = 'n_' + match_type
        for player in players: self._players[player][n_what] += 1

    def _update_players_last_tournament (self, players, tournament, date):

        dateTime = datetime.strptime(date, '%b %Y')
        for player in players:
            last_tournament_dateTime = self._players[player]['last_tournament_dateTime']
            if last_tournament_dateTime is None or last_tournament_dateTime < dateTime:
                self._players[player]['last_tournament'] = tournament
                self._players[player]['last_tournament_date'] = date
                self._players[player]['last_tournament_dateTime'] = dateTime
            
    def _players__from_dict_to_df (self):
        
        self.players['player'] = list(self._players.keys())
        self.players['player_idx'] = [self._players[player]['idx'] for player in self.players['player']]
        self.players = pd.DataFrame(self.players)
        self.players.set_index('player_idx', inplace=True)
    
    def _init_abilities_to_100 (self):
        
        self.abilities = th.ones(self.n_players)*100.
    
    def _ranking__from_dict_to_df (self):
        
        self.ranking['player'] = list(self.players['player'])
        self.ranking['ability'] = self.abilities.tolist()
        self.ranking['n_singles'] = [self._players[player]['n_singles'] for player in self.ranking['player']]
        self.ranking['n_doubles'] = [self._players[player]['n_doubles'] for player in self.ranking['player']]
        self.ranking['n_tot'] = [ns+nd for ns, nd in zip(self.ranking['n_singles'], self.ranking['n_doubles'])]
        self.ranking['last_tournament'] = [self._players[player]['last_tournament'] for player in self.ranking['player']]
        self.ranking['last_tournament_date'] = [self._players[player]['last_tournament_date'] for player in self.ranking['player']]
        self.ranking['rank'] = list(range(1, self.n_players+1))
        self.ranking = pd.DataFrame(self.ranking)
        self.ranking.set_index('rank', inplace=True)
    
    def _rejected__from_dict_to_df (self):
        
        self.rejected = pd.DataFrame(self.rejected)
        self.rejected.set_index(['file', 'file_row'], inplace=True)
        
    def __repr__ (self):
    
        s = "TennisUniverse"
        s += f"\n  files: {self.files}"
        s += f"\n  n_accepted_rows: {len(self.df)-len(self.rejected)}"
        s += f"\n  n_rejected_rows: {len(self.rejected)}"
        s += f"\n  n_players: {self.n_players}"
        s += "\n  tournaments:"
        for t in self.tournaments: s += "\n    - '" + t + "'"
        return s
        
    def __str__ (self):
    
        return self.__repr__()
                
    
# ---------------------------------- utils ----------------------------------


_accepted_keys = {
    'players A': ['players a', 'players 1', 'giocatori a', 'giocatori 1'],
    'players B': ['players b', 'players 2', 'giocatori b', 'giocatori 2'],
    'score': ['score', 'risultato', 'punteggio'],
    'tournament': ['tournament', 'torneo']
}      
_here = os.path.dirname(os.path.abspath(__file__))
_tournaments_config = pd.read_csv(_here+"/tournaments_config.csv")
_tournaments_config.set_index('tournament', inplace=True)