import numpy as np


def normalize_weight(df):
    df['weightLbsTotal'] = np.where(df['weightLbsTotal'] < 1, 1, df['weightLbsTotal'])
    df['weightLbsTotal'] = df['weightLbsTotal'].round(0).astype(int)
    return df
