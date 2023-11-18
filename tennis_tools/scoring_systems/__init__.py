from .base import BasicBlock, p_from_abilities_formula
from .mrdodo import MrDodo, mrdodo_check_score
from .toringo import Toringo # toringo_check_score = mrdodo_check_score

get = {
    'mrdodo': MrDodo,
    'toringo': Toringo
}

check_if_admittable_score = {
    'mrdodo': mrdodo_check_score,
    'toringo': mrdodo_check_score
}