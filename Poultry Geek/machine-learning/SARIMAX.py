import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from statsmodels.tsa.statespace.sarimax import SARIMAX

import statsmodels.api as sm
import itertools
import pandas as pd


if __name__ == "__main__":
    """Entorno de pruebas para probar los algoritmos"""

