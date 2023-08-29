import torch as th
from scipy.special import binom
from math import pi
from ..utils import to_torch_tensor


# ----------------------------------------------------------------------------------------
#    p_from_abilities_formula
# ----------------------------------------------------------------------------------------


def p_from_abilities_formula (abilities):

    abilities = to_torch_tensor(abilities, th.float)
    if abilities.shape[-1] == 2:
        u = th.tensor([1., -1.], device=abilities.device)
    elif abilities.shape[-1] == 4:
        u = th.tensor([0.5, 0.5, -0.5, -0.5], device=abilities.device)
    else: raise Exception("abilities.shape[-1] must be in [2, 4]")
    return 0.5 + th.atan(0.1 * abilities @ u) / pi


# ----------------------------------------------------------------------------------------
#    BasicBlock
# ----------------------------------------------------------------------------------------

                
class BasicBlock:
    
    def __init__ (self, end, max_advantages=None):
        
        self.end = end
        self.max_advantages = max_advantages
        self.device = th.device('cpu')
        self._binom = th.tensor([binom(end-1+n, end-1) for n in range(end)]).float()
                
    def to (self, device):
        
        if self.device == device: pass
        else:
            self.device = device
            self._binom = self._binom.to(device)
        
    def proba (self, score_A, score_B, p_point_A, p_sudden_death_A=None):
    
        score_A = to_torch_tensor(score_A, th.long)
        score_B = to_torch_tensor(score_B, th.long)
        p = to_torch_tensor(p_point_A, th.float)
        psd = p_sudden_death_A if p_sudden_death_A is not None else p
        psd = to_torch_tensor(psd, th.float)
        self.to(score_A.device)
        
        e1 = self.end - 1
        minmin = th.minimum(score_A, score_B)
        if self.max_advantages is None: pass
        else: sudden_death_was_played = (minmin == e1+self.max_advantages)
        # minmin = min(min(A,B), end-1)
        # maxmin = max(min(A,B), end-1)
        maxmin = minmin*1
        minmin[minmin > e1] = e1 
        maxmin[maxmin < e1] = e1
        
        if self.max_advantages is None:
            return self._binom[minmin] * 2**(maxmin-e1) * p**score_A * (1-p)**score_B
        else: 
            Awin = (score_A > score_B)
            return self._binom[minmin] * 2**(maxmin-e1) * ( \
                   (~sudden_death_was_played) * p**score_A * (1-p)**score_B + \
                   sudden_death_was_played * (p*(1-p))**maxmin * (Awin*psd + (~Awin)*(1-psd)) \
                   )
        # Note: (score_A, score_B)=(0, 0) --> proba=1
        
    def proba_A_wins (self, p_point_A, p_sudden_death_A=None):
    
        p = to_torch_tensor(p_point_A, th.float)
        psd = p_sudden_death_A if p_sudden_death_A is not None else p
        psd = to_torch_tensor(psd, th.float)
        
        return self._proba_A_wins_without_advantages(p) + \
               self._proba_A_wins_during_regular_advantages(p) + \
               self._proba_A_wins_at_sudden_death_point(p, psd)
    
    def _proba_A_wins_without_advantages(self, p_point_A):

        p = p_point_A[..., None].expand(*p_point_A.size(), self.end-1)
        score_A = th.empty_like(p, dtype=th.long)
        score_B = th.empty_like(p, dtype=th.long)
        score_A[..., :] = th.tensor([self.end]*(self.end-1), device=p_point_A.device)
        score_B[..., :] = th.tensor(list(range(self.end-1)), device=p_point_A.device)
        return self.proba(score_A, score_B, p).sum(dim=-1)
    
    def _proba_A_wins_during_regular_advantages (self, p_point_A):
        
        if self.max_advantages == 0.: return 0.
        p = p_point_A
        e1 = self.end-1
        g = 2*p*(1-p)
        if self.max_advantages is not None: 
            return self._binom[e1] * p**(e1+2) * (1-p)**e1 * (1-g**self.max_advantages) / (1-g)
        else: 
            return self._binom[e1] * p**(e1+2) * (1-p)**e1 / (1-g)
    
    def _proba_A_wins_at_sudden_death_point (self, p_point_A, p_sudden_death_A):
        
        if self.max_advantages is None: return 0.
        else: 
            p = p_point_A
            psd = p_sudden_death_A
            e1 = self.end-1
            return self._binom[e1] * 2**self.max_advantages * \
                   (p*(1-p))**(e1+self.max_advantages) * psd
        
    def __repr__ (self):
        
        return f"BasicBlock(end={self.end}, max_advantages={self.max_advantages})"
    
    def __str__ (self):
        
        return self.__repr__()