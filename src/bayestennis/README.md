# Bayes Tennis Package

The `bayestennis` package provides a simple framework to estimate the abilities of tennis players based on a given dataset of tennis matches.

## Quick Guide

The main object of the package is the `TennisUniverse` class. The workflow is as follows:

1. Initialize a `TennisUniverse` object with a `TennisDataFrame` containing the data.
2. Perform optimization with the `optimize` method.

A `TennisDataFrame` is a pandas DataFrame with specific columns (see `structures.py`). The `io` module provides functions to import a `TennisDataFrame` from various sources.

```python
from bayestennis.io import import_notion_csv
from bayestennis import TennisUniverse

tennisDataFrame = import_notion_csv("path/to/file.csv")
tennisUniverse = TennisUniverse(tennisDataFrame)
tennisUniverse.optimize()

# View the results
tennisUniverse.playersDataFrame
```

## Tutorial

Please refer to the external tutorial for an example of how to use the package.
