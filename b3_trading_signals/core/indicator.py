"""
Indicator - Geração de indicadores técnicos para backtesting B3
"""

import pandas as pd
import numpy as np


class Indicator:
    """Calcula indicadores técnicos sobre um DataFrame OHLCV."""

    def __init__(self, strategy: dict):
        self.ind_t = strategy["ind_t"]
        self.ind_p = strategy["ind_p"]

    def setup_indicator(self, df: pd.DataFrame) -> pd.DataFrame:
        ind_t = self.ind_t
        ind_p = self.ind_p

        if ind_t == "SMA":
            for p in ind_p:
                df[f"MA_{p}"] = df["Close"].rolling(window=p, min_periods=1).mean()

        elif ind_t == "EMA":
            for p in ind_p:
                df[f"MA_{p}"] = df["Close"].ewm(span=p, adjust=False).mean()

        elif ind_t == "WMA":
            for p in ind_p:
                weights = np.arange(1, p + 1)
                df[f"MA_{p}"] = (
                    df["Close"]
                    .rolling(window=p, min_periods=1)
                    .apply(lambda x: np.dot(x, weights[-len(x):]) / weights[-len(x):].sum(), raw=True)
                )

        elif ind_t == "BB":
            period = int(ind_p[0])
            std_mult = float(ind_p[1])
            df["BB_mid"] = df["Close"].rolling(window=period, min_periods=1).mean()
            df["BB_std"] = df["Close"].rolling(window=period, min_periods=1).std().fillna(0)
            df["BB_upper"] = df["BB_mid"] + std_mult * df["BB_std"]
            df["BB_lower"] = df["BB_mid"] - std_mult * df["BB_std"]

        elif ind_t == "MACD":
            fast, slow, signal = int(ind_p[0]), int(ind_p[1]), int(ind_p[2])
            ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
            ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
            df["MACD_line"] = ema_fast - ema_slow
            df["MACD_signal"] = df["MACD_line"].ewm(span=signal, adjust=False).mean()
            df["MACD_hist"] = df["MACD_line"] - df["MACD_signal"]

        return df
