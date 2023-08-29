import torch as th
from ..utils import to_torch_tensor


# ---------------------------------------------------------------------------------------------
#    L1_Regularization
# ---------------------------------------------------------------------------------------------


class L1_Regularization:
    
    def __init__ (self, bandwidth):
        
        if bandwidth <= 0: raise Exception("bandwidth > 0 must be True")
        self.bandwidth = bandwidth
        
    def __call__ (self, abilities):  
        
        abilities = to_torch_tensor(abilities, th.float)
        return th.sum(abilities.abs()) * 2 / self.bandwidth
            
    def __repr__ (self):
        
        return f"L1_Regularization(bandwidth={self.bandwidth})"
    
    def __str__ (self):
        
        return self.__repr__()
        

# ---------------------------------------------------------------------------------------------
#    L2_Regularization
# ---------------------------------------------------------------------------------------------


class L2_Regularization:
    
    def __init__ (self, bandwidth):
        
        if bandwidth <= 0: raise Exception("bandwidth > 0 must be True")
        self.bandwidth = bandwidth
        
    def __call__ (self, abilities):  
        
        abilities = to_torch_tensor(abilities, th.float)
        return th.sum(abilities**2) / 2 / self.bandwidth**2
            
    def __repr__ (self):
        
        return f"L2_Regularization(bandwidth={self.bandwidth})"
    
    def __str__ (self):
        
        return self.__repr__()