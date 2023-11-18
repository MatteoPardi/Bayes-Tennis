import torch as th
from .base import BasicBlock, p_from_abilities_formula
from ..utils import to_torch_tensor


# --------------------------------------------------------------------------------------------
#    Toringo (Scoring System)
# --------------------------------------------------------------------------------------------


class Toringo:

    def __init__ (self):
        
        self.game = BasicBlock(end=4, max_advantages=None)
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
    
        s = "Scoring System 'Toringo':\n"
        s += "  Game: " + repr(self.game) + "\n"
        s += "  TieBreak(Set): " + repr(self.set_tie_break) + "\n"
        s += "  Set: " + repr(self.set) + "\n"
        s += "  TieBreak(Match): " + repr(self.match_tie_break) + "\n"
        s += "  Match: " + repr(self.match)
        return s
        
    def __str__ (self):
    
        return self.__repr__()
        
        
# --------------------------------------------------------------------------------------------
#    toringo_check_score 
# --------------------------------------------------------------------------------------------

'''
    use mrdodo_check_score. It's ok also for Toringo
'''