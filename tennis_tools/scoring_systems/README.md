## Guide to create a new scoring system
Please look at the `MrDodo` scoring system to see an example, defined in the python module `mrdodo.py`.

A 'scoring system' is a class satisfying the following template:
```python
class MyScoringSystem:

	def proba (self, score, abilities):
	# <...>
	
	def proba_A_wins (self, abilities):
	# <...>
```
Here `abilities` and `score` are `torch.Tensor`s having the same shape, except in the last dimension:
- `abilities.shape[-1]` = `2` (singles) or `4` (doubles).
- `score.shape[-1]` depends on the scoring system, and the formalism chosen to report the score.

The other dimensions are used to work with batches of matches.

Utilization:
- `proba(score, abilities)` computes the probability of that score according to those abilities.
- `proba_A_wins(abilities)` computes the probability that player(s) A wins the match according to those abilities.

### Check Score Function

Each scoring system must be defined togheter with its corresponding 'check score function', a function satisfying the following template:
```python
def myscoringsystem_check_score (score):
# <...>
```
Here `score` is a list of int. Utilization: `myscoringsystem_check_score(score)` returns `False` if the new scoring systems doesn't recognize the score as admittable, else returns `score`, or a preprocessed version of it (ready to be passed to `TennisUniverse.loss.add(<...>)`.

### Make it available

Eventually, to make the new scoring system ready to be used, modify `__init__.py` in this way (let's assume we defined the new scoring system in a file called `myscoringsystem.py`):
```python
# tennis_tools/scoring_systems/__init__.py
from .base import BasicBlock, p_from_abilities_formula
from .mrdodo import MrDodo, mrdodo_check_score
from .myscoringsystem import MyScoringSystem, myscoringsystem_check_score # <---

get = {
    'mrdodo': MrDodo,
	'myscoringsystem': MyScoringSystem # <---
}

check_if_admittable_score = {
    'mrdodo': mrdodo_check_score,
	'myscoringsystem': myscoringsystem_check_score # <---
}
```
Now the new scoring system is ready to be used: `myscoringsystem` will be its name.