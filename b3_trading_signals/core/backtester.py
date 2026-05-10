"""
Backtester - Motor de backtesting para estratégias B3
"""

import json
import numpy as np
import pandas as pd

from .strategies import Strategies


class Backtester:
    """Executa backtesting de estratégias sobre dados históricos."""

    def __init__(self, df: pd.DataFrame, file_config: str = None):
        self.df = df.copy()
        self.config = {}
        if file_config:
            try:
                with open(file_config) as f:
                    self.config = json.load(f)
            except Exception:
                pass
        self.initial_capital = self.config.get("backtest", {}).get("initial_capital", 10000)

    def run_strategy(self, strategy: dict) -> pd.DataFrame:
        df = Strategies.generate_signal(self.df, strategy)

        # Posição: apenas long, deslocada 1 período (sem lookahead)
        df["Position"] = df["Signal"].shift(1).fillna(0).clip(0, 1)

        # Retornos
        df["Market_Return"] = df["Close"].pct_change().fillna(0)
        df["Strategy"] = (df["Position"] * df["Market_Return"]).fillna(0)

        # Cumulativos
        df["Cumulative_Strategy"] = (1 + df["Strategy"]).cumprod()
        df["Cumulative_Market"] = (1 + df["Market_Return"]).cumprod()

        # Trades (mudança de posição)
        df["Trade"] = df["Position"].diff().abs().fillna(0)
        df["Trade"] = (df["Trade"] > 0).astype(int)
        df["Cumulative_Trades"] = df["Trade"].cumsum()

        # Drawdown
        df["Running_Max"] = df["Cumulative_Strategy"].cummax()
        df["Drawdown"] = (
            (df["Cumulative_Strategy"] - df["Running_Max"]) / df["Running_Max"]
        ).fillna(0)

        return df
