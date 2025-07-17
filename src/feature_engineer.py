# ENERGY-GENERATION-PREDICTION-DASHBOAR/src/feature_engineer.py
# This file should contain the full code for SolarFeatureEngineer and its dependencies.

import pandas as pd
import numpy as np
import math

from statsmodels.tsa.stattools import adfuller, kpss
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
# If RandomForestRegressor, TimeSeriesSplit, cross_val_score are *not* used within the class methods,
# you can omit them from this file to keep it cleaner. Otherwise, include them.
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import TimeSeriesSplit, cross_val_score


# AUXILIARY FUNCTIONS
def identify_non_stationary(df, alpha=0.05):
    # ... (your existing code for this function) ...
    non_stat = []
    for col in df.select_dtypes('number').columns:
        s = df[col].dropna()
        if len(s) < 10:
            continue
        try:
            p_adf = adfuller(s)[1]
            p_kpss = kpss(s, nlags='auto')[1]
        except:
            non_stat.append(col)
            continue
        if p_adf >= alpha or p_kpss <= alpha:
            non_stat.append(col)
    return non_stat

def compute_best_lags(df, target='generation', max_lag=24):
    # ... (your existing code for this function) ...
    vars_ = [c for c in df.select_dtypes('number').columns if c != target]
    xcorr = pd.DataFrame({
        v: [df[target].corr(df[v].shift(l)) for l in range(max_lag+1)]
        for v in vars_
    }, index=range(max_lag+1))
    return {v: int(xcorr[v].abs().idxmax()) for v in vars_}

def add_temporal_features(df):
    # ... (your existing code for this function) ...
    df = df.copy()
    idx = df.index
    df['hour']      = idx.hour
    df['hour_sin'] = np.sin(2*np.pi * df['hour']/24)
    df['hour_cos'] = np.cos(2*np.pi * df['hour']/24)
    df['dow']      = idx.dayofweek
    df['dow_sin']  = np.sin(2*np.pi * df['dow']/7)
    df['dow_cos']  = np.cos(2*np.pi * df['dow']/7)
    df['month']    = idx.month
    df['month_sin']= np.sin(2*np.pi * df['month']/12)
    df['month_cos']= np.cos(2*np.pi * df['month']/12)
    return df

# CUSTOM TRANSFORMER CLASS
class SolarFeatureEngineer(BaseEstimator, TransformerMixin):
    # ... (your existing code for SolarFeatureEngineer class) ...
    def __init__(self,
                 target='generation',
                 max_lag=24,
                 roll_windows=None,
                 log_transform_cols=None):
        self.target = target
        self.max_lag = max_lag
        self.roll_windows = roll_windows or [3,6,24]
        self.log_transform_cols = log_transform_cols or []

    def fit(self, X, y=None):
        self.non_stat_vars_ = identify_non_stationary(X)
        self.best_lags_    = compute_best_lags(X, target=self.target, max_lag=self.max_lag)
        return self

    def transform(self, X):
        df = X.copy()
        clip_q = [0.001, 0.999]
        num = df.select_dtypes('number').columns.drop(
            [self.target, f"{self.target}_log1p"], errors='ignore'
        )
        lowers = df[num].quantile(clip_q[0])
        uppers = df[num].quantile(clip_q[1])
        df[num] = df[num].clip(lower=lowers, upper=uppers, axis=1)
        for col in self.non_stat_vars_:
            df[f"{col}_diff1"] = df[col].diff(1)
        for col, lag in self.best_lags_.items():
            if col == self.target: continue
            df[f"{col}_lag{lag}"] = df[col].shift(lag)
        for col in num:
            df[f"{col}_lag24"] = df[col].shift(24)
        numeric = df.select_dtypes('number').columns.drop(
            [self.target, f"{self.target}_log1p"], errors='ignore'
        )
        for w in self.roll_windows:
            for col in numeric:
                df[f"{col}_roll{w}h"] = df[col].rolling(window=w, min_periods=1).mean()
        for col in ['shortwave_radiation', 'global_tilted_irradiance']:
            if col in df:
                df[f"{col}_sq"] = df[col]**2
        if {'diffuse_radiation','global_tilted_irradiance'}.issubset(df.columns):
            df['diffuse_ratio'] = df['diffuse_radiation'] / (df['global_tilted_irradiance']+1e-6)
        df = add_temporal_features(df)
        for col in self.log_transform_cols:
            if col in df:
                df[f"{col}_log1p"] = np.log1p(df[col])
        drop_cols = list(self.non_stat_vars_)
        df = df.drop(columns=drop_cols, errors='ignore')
        df = df.dropna()
        self.feature_names_ = df.columns.tolist()
        return df

    def get_feature_names_out(self):
        return self.feature_names_