import numpy as np
import math
import pandas as pd


def geo_to_cartesian(df: pd.DataFrame, lat_col: str, lon_col: str, out_prefix: str) -> pd.DataFrame:
    """
    Generates cartesian coordinates from a latitude and longitude column and inserts them as new columns
    :param df: DataFrame containing latitude and longitude columns
    :param lat_col: Name of the latitude column in the DataFrame
    :param lon_col: Name of the longitude column in the DataFrame
    :param out_prefix: Prefix for the output Cartesian coordinate columns
    :return: None
    """
    df[out_prefix + 'X'] = np.cos(df[lat_col] * math.pi / 180.0) * np.cos(df[lon_col] * math.pi / 180.0)
    df[out_prefix + 'Y'] = np.cos(df[lat_col] * math.pi / 180.0) * np.sin(df[lon_col] * math.pi / 180.0)
    df[out_prefix + 'Z'] = np.sin(df[lat_col] * math.pi / 180.0)
    return df
