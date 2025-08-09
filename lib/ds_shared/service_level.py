import pandas as pd


def unify_service_levels(df):
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: 'Same Day' if sl == 'Same-Day' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: 'Same Day' if sl == 'Same Day Anytime' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: '90 Minute' if sl == 'Xpress' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: '90 Minute' if sl == '90 minute' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: '90 Minute' if sl == '90 Minutes' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: '3 Hour' if sl == '180 Minute' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: '30 Minute' if sl == '30-minute-sla-manual' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: '30 Minute' if sl == 'hotshot-asap-manual' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: 'Same Day' if sl == 'Christmas Tree - Same Day' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: '3 Hour' if sl == 'OLD - 180 Minute' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: '300 Minute' if sl == '300 Minute - PRO' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: '120 Minute' if sl == '120 Minute - PRO' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: '90 Minute' if sl == '90 Minute - PRO' else sl)
    df['serviceLevel'] = df['serviceLevel'].apply(lambda sl: '3 Hour' if sl == '180 Minute - PRO' else sl)

    all_sls = df['serviceLevel'].unique().tolist()
    df['serviceLevel'] = df['serviceLevel'].astype(pd.CategoricalDtype(categories=all_sls))

    return df, all_sls


lp_sla_time_in_minutes = {
    'Same Day': 5 * 60,
    '3 Hour': 3 * 60,
    '120 Minute': 120,
    '90 Minute': 90,
    '4 Hour': 4 * 60,
    '30 Minute': 30,
    '300 Minute': 300
}