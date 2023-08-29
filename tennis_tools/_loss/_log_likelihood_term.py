import torch as th
from ..utils import to_torch_tensor


# ---------------------------------------------------------------------------------------------
#    LogLikelihoodTerm
# ---------------------------------------------------------------------------------------------


class LogLikelihoodTerm:
    
    def __init__ (self, scoring_system):
        
        self.scoring_system = scoring_system
        self.score = None
        self.players_idx = None
        self.passed_months = None
        self.weights = None
        self.n_samples = 0
        self.device = th.device('cpu')
        
    def __call__ (self, abilities):  
        
        if self.players_idx is None or self.score is None or self.weights is None: return 0.
        abilities = to_torch_tensor(abilities, th.float)
        self.to(abilities.device)
        abilities = abilities[self.players_idx]        
        return -th.sum(th.log(self.scoring_system.proba(self.score, abilities) + 1e-40) * self.weights)
    
    def add (self, new_score, new_players_idx, new_passed_months):
        
        new_score = self._to_2dim(to_torch_tensor(new_score, th.long).to(self.device))
        new_players_idx = self._to_2dim(to_torch_tensor(new_players_idx, th.long).to(self.device))
        new_passed_months = to_torch_tensor(new_passed_months, th.long).to(self.device).reshape(-1)
        if new_score.shape[0] != new_players_idx.shape[0]:
            raise Exception("new_score.shape[0] == new_players_idx.shape[0] must be True")
        if new_score.shape[0] != new_passed_months.shape[0]:
            raise Exception("new_score.shape[0] == new_passed_months.shape[0] must be True")
        
        if self.score is None: self.score = new_score.clone()
        else: self.score = th.cat([self.score, new_score], dim=0)
        if self.players_idx is None: self.players_idx = new_players_idx.clone()
        else: self.players_idx = th.cat([self.players_idx, new_players_idx], dim=0)  
        if self.passed_months is None: self.passed_months = new_passed_months.clone()
        else: self.passed_months = th.cat([self.passed_months, new_passed_months], dim=0) 
        if self.weights is None: self.weights = th.ones_like(new_passed_months)
        else: self.weights = th.cat([self.weights, th.ones_like(new_passed_months)], dim=0) 
        
        self.n_samples = self.score.shape[0]
        return self
        
    def set_weights (self, half_time, months_shift):
    
        self.weights = 2**(-(self.passed_months-months_shift)/half_time)
        self.weights[self.weights > 1.] = 0.

    def to (self, device):
        
        if self.device == device: pass
        else:
            self.device = device
            self.score = self.score.to(device)
            self.players_idx = self.players_idx.to(device)
            self.passed_months = self.passed_months.to(device)
            self.weights = self.weights.to(device)
            
    def _to_2dim (self, x):
        
        if x.dim() == 2: return x
        elif x.dim() == 1: return x[None, :]
        else: raise Exception("x.dim() must be in [1, 2]")
            
    def __repr__ (self):
        
        s = f"LogLikelihoodTerm:"
        s += f"\n  scoring_system: '{self.scoring_system.__class__.__name__}'"
        s += f"\n  n_samples: {self.n_samples}"
        return s
    
    def __str__ (self):
        
        return self.__repr__()