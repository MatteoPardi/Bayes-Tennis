import torch as th
from ..utils import to_torch_tensor
from ._log_likelihood_term import LogLikelihoodTerm
from ._regularization_term import L1_Regularization, L2_Regularization
from .. import scoring_systems


# ------------------------------------------------------------------------------------
#    Loss
# ------------------------------------------------------------------------------------


class Loss:
    
    def __init__ (self, regularization='L2', bandwidth=5.):
        
        self.terms = {'regularization': _get_regularization(regularization, bandwidth)}
        
    def __call__ (self, abilities):
        
        tot = 0.
        for _, term in self.terms.items(): tot = tot + term(abilities)
        return tot
    
    def add (self, scoring_system_name, new_score, new_players_idx, new_passed_months):
        
        if scoring_system_name not in self.terms: 
            new_scoring_system = scoring_systems.get[scoring_system_name]
            self.terms[scoring_system_name] = LogLikelihoodTerm(new_scoring_system())
        self.terms[scoring_system_name].add(new_score, new_players_idx, new_passed_months)
        
    def set_weights (self, half_time=8, months_shift='last played'):
    
        if months_shift == 'last played': months_shift = self._get_last_played_month()
        for name, term in self.terms.items():
            if name == 'regularization': pass
            else: term.set_weights(half_time, months_shift)
            
    def _get_last_played_month (self):
    
        _min = float('inf')
        for name, term in self.terms.items():
            if name == 'regularization': pass
            else: 
                _new_candidate = term.passed_months.min().item()
                if _new_candidate < _min: _min = _new_candidate
        return _min         
        
    def __repr__ (self):
        
        s = "Loss Function. Terms:"
        for key, val in self.terms.items():
            s += "\n" + key + ": " + str(val)
        return s
    
    def __str__ (self):
        
        return self.__repr__()  


# ------------------------------------- utils -------------------------------------


def _get_regularization (regularization, bandwidth):

    if regularization == 'L1': return L1_Regularization(bandwidth)
    if regularization == 'L2': return L2_Regularization(bandwidth)