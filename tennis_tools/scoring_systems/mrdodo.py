import torch as th
from .base import BasicBlock, p_from_abilities_formula
from ..utils import to_torch_tensor


# --------------------------------------------------------------------------------------------
#    MrDodo (Scoring System)
# --------------------------------------------------------------------------------------------


class MrDodo:

    def __init__ (self):
        
        self.game = BasicBlock(end=4, max_advantages=1)
        self.set_tie_break = BasicBlock(end=7)
        self.set = BasicBlock(end=6, max_advantages=1)
        self.match_tie_break = BasicBlock(end=10)
        self.match = BasicBlock(end=2, max_advantages=0)
        
    def proba (self, score, abilities):
    
        abilities = to_torch_tensor(abilities, th.float)
        score = to_torch_tensor(score, th.long)
        if score.shape[-1] != 6: raise Exception("score.shape[-1] == 6 must be True")
    
        p_point_A = p_from_abilities_formula(abilities)
        p_game_A = self.game.proba_A_wins(p_point_A)
        p_set_tie_break_A = self.set_tie_break.proba_A_wins(p_point_A)
        
        return self.set.proba(score[..., 0], score[..., 1], p_game_A, p_set_tie_break_A) * \
               self.set.proba(score[..., 2], score[..., 3], p_game_A, p_set_tie_break_A) * \
               self.match_tie_break.proba(score[..., 4], score[..., 5], p_point_A)
               
    def proba_A_wins (self, abilities):
    
        abilities = to_torch_tensor(abilities, th.float)
    
        p_point_A = p_from_abilities_formula(abilities)
        p_game_A = self.game.proba_A_wins(p_point_A)
        p_set_tie_break_A = self.set_tie_break.proba_A_wins(p_point_A)
        p_set_A = self.set.proba_A_wins(p_game_A, p_set_tie_break_A)
        p_match_tie_break_A = self.match_tie_break.proba_A_wins(p_point_A)
        return self.match.proba_A_wins(p_set_A, p_match_tie_break_A)
        
    def __repr__ (self):
    
        s = "Scoring System 'MrDodo':\n"
        s += "  Game: " + repr(self.game) + "\n"
        s += "  TieBreak(Set): " + repr(self.set_tie_break) + "\n"
        s += "  Set: " + repr(self.set) + "\n"
        s += "  TieBreak(Match): " + repr(self.match_tie_break) + "\n"
        s += "  Match: " + repr(self.match)
        return s
        
    def __str__ (self):
    
        return self.__repr__()
        
        
# --------------------------------------------------------------------------------------------
#    mrdodo_check_score
# --------------------------------------------------------------------------------------------
# (I don't like how I implemented it... I intend to change it soon)


def mrdodo_check_score (score):
    
    if len(score) == 4: score += [0,0] # preprocess
    if len(score) != 6: return False
    set_1 = _check_set(score[0], score[1])
    if set_1 is None: return False
    set_2 = _check_set(score[2], score[3])
    if set_2 is None: return False
    match_tie_break = _check_match_tie_break(score[4], score[5])
    if match_tie_break is None: return False
    
    _list = [set_1, set_2, match_tie_break]   
    if _list == ['A win', 'A win', 'no tie break']: return score
    if _list == ['B win', 'B win', 'no tie break']: return score
    if _list == ['A win', 'B win', 'A win']: return score
    if _list == ['A win', 'B win', 'B win']: return score
    if _list == ['B win', 'A win', 'A win']: return score
    if _list == ['B win', 'A win', 'B win']: return score
    return False


# ----------------------------------- utils -----------------------------------     

    
def _check_set (a, b):

    _max = max(a,b)
    _min = min(a,b)
    if _min < 0: return None
    if _max not in [6,7]: return None
    if _max == 6 and _min > 4: return None
    if _max == 7 and _min not in [5,6]: return None
    if a > b: return 'A win'
    else: return 'B win'
    
def _check_match_tie_break (a, b):

    if a == 0 and b == 0: return 'no tie break'
    _max = max(a,b)
    _min = min(a,b)
    if _min < 0: return None
    if _max < 10: return None
    if _max == 10 and _min > 8: return None
    if _max > 10 and _min != _max-2: return None
    if a > b: return 'A win'
    else: return 'B win'