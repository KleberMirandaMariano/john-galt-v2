"""
Strategies - Geração de sinais de compra/venda para backtesting B3
"""

import pandas as pd
import numpy as np


class Strategies:
    """Gera sinais de trading a partir de indicadores técnicos."""

    @staticmethod
    def generate_signal(df: pd.DataFrame, strategy: dict) -> pd.DataFrame:
        ind_t = strategy["ind_t"]
        ind_p = strategy["ind_p"]
        df = df.copy()
        df["Signal"] = 0

        if ind_t in ("SMA", "EMA", "WMA"):
            periods = sorted(ind_p)
            if len(periods) >= 2:
                fast_col = f"MA_{periods[0]}"
                slow_col = f"MA_{periods[1]}"
                if fast_col in df.columns and slow_col in df.columns:
                    df.loc[df[fast_col] > df[slow_col], "Signal"] = 1
                    df.loc[df[fast_col] <= df[slow_col], "Signal"] = -1

        elif ind_t == "BB":
            if "BB_upper" in df.columns and "BB_lower" in df.columns:
                df.loc[df["Close"] < df["BB_lower"], "Signal"] = 1
                df.loc[df["Close"] > df["BB_upper"], "Signal"] = -1
                df["Signal"] = df["Signal"].replace(0, np.nan).ffill().fillna(0)

        elif ind_t == "MACD":
            if "MACD_line" in df.columns and "MACD_signal" in df.columns:
                df.loc[df["MACD_line"] > df["MACD_signal"], "Signal"] = 1
                df.loc[df["MACD_line"] <= df["MACD_signal"], "Signal"] = -1

        return df
