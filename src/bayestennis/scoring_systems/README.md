# Scoring Systems

The scoring systems submodule provides a framework for implementing and using different tennis scoring rules. Each scoring system defines how to compute probabilities for different match outcomes based on player abilities.

## Overview

A scoring system in tennis defines:
- How points are accumulated (games, sets, match)
- When a game/set/match is won, specifying special rules (advantages, tiebreaks, etc.)

The module includes:
- `BasicScoreBlock`: Core probability calculations for basic scoring units
- `ScoringSystem`: Abstract base class for implementing scoring systems
- Built-in systems:
  - `MrDodo`: Standard tennis scoring system used by Dodo Tennis Club in Lucca (Italy)
  - `Toringo`: Standard tennis scoring system used by Toringo Pierluigi Eligi Tennis Club in Lucca (Italy)

## Creating a New Scoring System

Please have a look at the existing scoring systems for inspiration and examples.

To create a new scoring system:

1. Create a new file in `scoring_systems/` (e.g., `MySystem.py`)
2. Inherit from `ScoringSystem` base class:

```python
from .base import BasicScoreBlock, ScoringSystem

class MySystem (ScoringSystem):
    def __init__(self, device=torch.device("cpu")):
        self.device = device
        # Define your scoring blocks
        self.game = BasicScoreBlock(score_end=4, n_max_advantages=1, device=device)
        self.set = BasicScoreBlock(score_end=6, n_max_advantages=1, device=device)
        # ...

    def to (self, device: torch.device):
        # Move internal tensors to specified device
        if self.device != device:
            self.device = device
            self.game.to(device)
            self.set.to(device)
            # Move other blocks...

    def process_score (self, score: list[int]):
        # Implement score validation
        pass

    def prob_this_score (self, score, abilities):
        # Implement score probability calculation
        pass

    def prob_teamA_wins (self, abilities):
        # Implement win probability calculation
        pass

    def __str__(self):
        return f"{self.__class__.__name__} scoring system"

    def __repr__(self):
        return f"{self.__class__.__name__}(device={self.device})"
```

3. Add your system to `__init__.py`:
```python
from .MySystem import MySystem
```

## Usage Example

```python
from bayestennis.scoring_systems import MrDodo

# Create scoring system
scoring = MrDodo()

# Check if a score is valid
score = [6, 4, 6, 2]  # Two sets: 6-4, 6-2
is_valid, normalized_score, winner_team = scoring.process_score(score)

# ...
```

## Key Components

### BasicScoreBlock
- Handles probability calculations for basic scoring units
- Parameters:
  - `score_end`: Points needed to win (e.g., 4 for games, 6 for sets)
  - `n_max_advantages`: Maximum number of advantages (None for infinite)

### ScoringSystem
Abstract base class with required methods:
- `process_score()`: Validates score format and values, and compute normalized score and winner team
- `prob_this_score()`: Calculates probability of a specific score
- `prob_teamA_wins()`: Calculates overall win probability
- `to()`: Moves internal tensors to specified device

See the docstrings in each class for detailed API documentation.
