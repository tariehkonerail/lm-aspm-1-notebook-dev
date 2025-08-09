from ds_shared.tzutil import get_local_time_components
import numpy as np
import pandas as pd


def augment_with_local_time(df, time_column='deliveryStartedAt'):

    time_components_df = df.apply(lambda row: get_local_time_components(row[time_column], row['fromLat'], row['fromLon']),
                  axis=1, result_type='expand')
    df = pd.concat([df, time_components_df], axis=1)
    return df


def cycle_encode(df, column, period):
    df[column + 'Sin'] = np.sin(2 * np.pi * df[column] / period)
    df[column + 'Cos'] = np.cos(2 * np.pi * df[column] / period)

    return df