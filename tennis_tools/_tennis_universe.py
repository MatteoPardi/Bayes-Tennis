import torch as th
from torch.optim.lr_scheduler import LambdaLR
from ._tennis_universe_base import TennisUniverse_Base
from .utils import tic, toc


# -------------------------------------------------------------------------------------
#    TennisUniverse
# -------------------------------------------------------------------------------------


class TennisUniverse (TennisUniverse_Base):
    
    def __init__ (self, *paths):
        
        super().__init__(*paths)
        
    def optimize (self, 
                  n_iter=1000, 
                  lr_start=1e-1, 
                  lr_end=1e-3, 
                  half_time=10, 
                  months_shift='last played',
                  device='cpu',
                  verbose=100):
        
        self.loss.set_weights(half_time=half_time, months_shift=months_shift)
        if not th.cuda.is_available() and device.startswith('cuda'):
            raise Exception("cuda is not available")
        device = th.device('cuda' if th.cuda.is_available() else 'cpu')
        
        abilities = th.zeros(self.n_players, device=device)
        optim = th.optim.Adam([abilities], lr=lr_start)
        lr_policy = LR_Exponential_Policy(lr_start, lr_end, n_iter)
        optim_scheduler = LambdaLR(optim, lr_lambda=lr_policy)
        
        abilities.requires_grad_(True)
        tic()
        if verbose: print(f"Optimization started. n_iter = {n_iter}")
        for n in range(n_iter):
            loss = self.loss(abilities)
            optim.zero_grad()
            loss.backward()
            optim.step()
            optim_scheduler.step()
            if verbose and not n % verbose: print(f" n {n}: loss = {loss}")
        if verbose: print(f" n {n+1}: loss = {loss} (end)")
        toc()
        abilities.requires_grad_(False)
        abilities = abilities.cpu()
        
        self.abilities = abilities - abilities.quantile(0.5) + 100. # median == 100
        self._update_abilities_in_ranking()
        self._sort_ranking()

    def _update_abilities_in_ranking (self):
        
        self.ranking['ability'] = self.ranking.apply(self._lambda_player_ability, axis=1)
        
    def _lambda_player_ability (self, row):

        return self.abilities[self._players[row['player']]['idx']].item()
    
    def _sort_ranking (self):
        
        self.ranking.sort_values('ability', ascending=False, inplace=True)
        i = {old: new for old, new in zip(self.ranking.index, range(1, 1+len(self.ranking.index)))}
        self.ranking.rename(index=i, inplace=True)        
        
        
# ------------------------------- utils -------------------------------
        
        
class LR_Exponential_Policy:
    
    def __init__ (self, lr_start, lr_end, n_iter):
        
        self.ratio = lr_end/lr_start
        self.tau = n_iter - 1
        if self.tau: self.base = self.ratio**(1/self.tau)
        
    def __call__ (self, n):
        
        if n < self.tau: return self.base**n
        else: return self.ratio