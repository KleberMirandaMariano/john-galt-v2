#!/usr/bin/env python3
"""
bayesian_signals.py — Sinais de trading com atualização Bayesiana + Kelly integrado.

Atualiza P(sucesso | evidências) sequencialmente à medida que novos sinais são
observados. O posterior alimenta o Kelly Criterion para sizing final.

Uso standalone:
    python3 src/bayesian_signals.py COGN3

Uso como módulo:
    from src.bayesian_signals import BayesianUpdater, SIGNALS_B3, bayesian_kelly

    updater = BayesianUpdater(prior=0.50)
    updater.update_from_library("mm20_breakup", SIGNALS_B3)
    updater.update_from_library("volume_spike", SIGNALS_B3)
    f_full, f_capped = bayesian_kelly(updater.posterior, ganho=2.0, perda=1.0)
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Likelihoods pré-calibrados para ações B3
# Formato: (P(E | H verdadeiro), P(E | H falso))
# H = "trade bem-sucedido no horizonte de 5 dias úteis"
# ---------------------------------------------------------------------------
SIGNALS_B3: Dict[str, Tuple[float, float]] = {
    "mm20_breakup":       (0.65, 0.35),  # rompe MM20 para cima
    "mm20_breakdown":     (0.28, 0.62),  # rompe MM20 para baixo (sinal negativo)
    "volume_spike":       (0.60, 0.35),  # volume > 2× média 20d
    "rsi_oversold":       (0.48, 0.22),  # RSI < 30 (sinal contrário)
    "rsi_overbought":     (0.22, 0.48),  # RSI > 70 (sinal contrário negativo)
    "iv_hv_low":          (0.60, 0.40),  # IV/HV < 0.8 → vol barata, favorável a compra
    "iv_hv_high":         (0.35, 0.60),  # IV/HV > 1.2 → vol cara, favorável a venda
    "macd_crossover_up":  (0.58, 0.38),  # MACD cruza sinal para cima
    "macd_crossover_down":(0.35, 0.60),  # MACD cruza sinal para baixo
    "ibov_positive":      (0.65, 0.42),  # Ibovespa positivo no dia
    "above_vwap":         (0.62, 0.40),  # preço acima VWAP intraday
    "selic_restrictive":  (0.38, 0.55),  # Selic ≥ 12% (custo de oportunidade alto)
}

SIGNALS_CRIPTO: Dict[str, Tuple[float, float]] = {
    "fng_extreme_fear":    (0.55, 0.35),  # FNG < 25 — oportunidade contrária
    "fng_extreme_greed":   (0.28, 0.55),  # FNG > 75 — sinal de topo
    "fng_neutral":         (0.50, 0.50),  # FNG 45-55 — sem edge
    "btc_dom_high":        (0.38, 0.55),  # BTC dom > 55% = risk-off altcoins
    "btc_dom_low":         (0.60, 0.42),  # BTC dom < 45% = risk-on altcoins
    "funding_positive":    (0.38, 0.58),  # funding rate positivo = mercado longo
    "funding_negative":    (0.60, 0.38),  # funding rate negativo = mercado curto
    "iv_hv_low":           (0.60, 0.40),  # IV/HV < 0.8 → vol barata
    "iv_hv_high":          (0.35, 0.60),  # IV/HV > 1.2 → vol cara
    "btc_above_ma20":      (0.65, 0.38),  # BTC acima da MM20
    "oi_spike":            (0.55, 0.38),  # OI spike > 20% em 24h
    "fred_restrictive":    (0.35, 0.55),  # Fed Funds ≥ 5% — risk-off global
}

# Likelihoods por regime para o detector de regime de mercado
REGIME_LIKELIHOODS: Dict[str, Dict[str, float]] = {
    "mm20_breakup":        {"trending": 0.70, "reverting": 0.25, "volatile": 0.45},
    "mm20_breakdown":      {"trending": 0.65, "reverting": 0.30, "volatile": 0.45},
    "volume_spike":        {"trending": 0.55, "reverting": 0.40, "volatile": 0.75},
    "rsi_oversold":        {"trending": 0.25, "reverting": 0.70, "volatile": 0.50},
    "rsi_overbought":      {"trending": 0.25, "reverting": 0.70, "volatile": 0.50},
    "iv_hv_high":          {"trending": 0.35, "reverting": 0.40, "volatile": 0.80},
    "iv_hv_low":           {"trending": 0.55, "reverting": 0.55, "volatile": 0.25},
    "macd_crossover_up":   {"trending": 0.65, "reverting": 0.30, "volatile": 0.45},
    "macd_crossover_down": {"trending": 0.65, "reverting": 0.30, "volatile": 0.45},
}


# ---------------------------------------------------------------------------
# Aplicação 1 e 2 — BayesianUpdater: atualização sequencial
# ---------------------------------------------------------------------------

@dataclass
class SignalRecord:
    name: str
    p_given_true: float
    p_given_false: float
    posterior_after: float
    likelihood_ratio: float


class BayesianUpdater:
    """
    Atualização sequencial de P(H) usando Teorema de Bayes.

    Cada update() usa o posterior atual como novo prior (Bayes sequencial).
    Mantém histórico completo para auditoria.

    Invariante: prior nunca pode ser 0 ou 1 — Bayes não atualiza certezas.
    """

    def __init__(self, prior: float = 0.50):
        if not 0.0 < prior < 1.0:
            raise ValueError(f"prior={prior} inválido — deve ser em (0, 1) exclusivo")
        self._initial_prior = prior
        self._posterior = prior
        self.history: List[SignalRecord] = []

    @property
    def posterior(self) -> float:
        return self._posterior

    @property
    def initial_prior(self) -> float:
        return self._initial_prior

    @property
    def n_signals(self) -> int:
        return len(self.history)

    def update(
        self,
        p_given_true: float,
        p_given_false: float,
        name: str = "unnamed",
    ) -> float:
        """
        P(H|E) = P(E|H)×P(H) / [P(E|H)×P(H) + P(E|¬H)×(1-P(H))]

        Args:
            p_given_true:  P(E|H)  — prob do sinal quando H é verdadeiro
            p_given_false: P(E|¬H) — prob do sinal quando H é falso
            name:          rótulo para histórico e debug

        Returns:
            Posterior P(H|E) após este update
        """
        if not (0 < p_given_true < 1 and 0 < p_given_false < 1):
            raise ValueError(
                f"Likelihoods devem ser em (0,1). "
                f"Recebido: P(E|H)={p_given_true}, P(E|¬H)={p_given_false}"
            )

        p_h     = self._posterior
        p_not_h = 1.0 - p_h

        numerator   = p_given_true  * p_h
        denominator = numerator + p_given_false * p_not_h

        if denominator == 0:
            return self._posterior

        lr = p_given_true / p_given_false
        self._posterior = round(numerator / denominator, 8)

        self.history.append(SignalRecord(
            name=name,
            p_given_true=p_given_true,
            p_given_false=p_given_false,
            posterior_after=self._posterior,
            likelihood_ratio=round(lr, 4),
        ))
        return self._posterior

    def update_from_library(
        self,
        signal_name: str,
        library: Dict[str, Tuple[float, float]],
    ) -> float:
        """Atalho: atualiza usando sinal pré-calibrado da biblioteca."""
        if signal_name not in library:
            available = ", ".join(library.keys())
            raise KeyError(f"Sinal '{signal_name}' não encontrado. Disponíveis: {available}")
        p_t, p_f = library[signal_name]
        return self.update(p_t, p_f, name=signal_name)

    def cumulative_lr(self) -> float:
        """Likelihood Ratio cumulativo (produto de todos os LRs individuais)."""
        lr = 1.0
        for s in self.history:
            lr *= s.likelihood_ratio
        return round(lr, 4)

    def reset(self, new_prior: Optional[float] = None):
        """Reseta para novo ativo ou nova sessão."""
        self._initial_prior = new_prior or self._initial_prior
        self._posterior = self._initial_prior
        self.history.clear()

    def summary(self) -> str:
        lines = [
            f"{'Sinal':<26} {'P(E|H)':>8} {'P(E|¬H)':>8} {'LR':>6} {'Posterior':>10}",
            "─" * 62,
            f"{'[prior inicial]':<26} {'':>8} {'':>8} {'':>6} {self._initial_prior:>9.2%}",
        ]
        for s in self.history:
            lines.append(
                f"{s.name:<26} {s.p_given_true:>8.3f} {s.p_given_false:>8.3f} "
                f"{s.likelihood_ratio:>6.3f} {s.posterior_after:>9.2%}"
            )
        lines += [
            "─" * 62,
            f"  LR cumulativo: {self.cumulative_lr():.4f}  │  "
            f"Sinais aplicados: {self.n_signals}  │  "
            f"Posterior final: {self._posterior:.2%}",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Aplicação 3 — Bayes + Kelly Criterion
# ---------------------------------------------------------------------------

def bayesian_kelly(
    posterior: float,
    ganho: float,
    perda: float = 1.0,
    risk_type: str = "high",
) -> Tuple[float, float, float]:
    """
    Kelly Criterion usando posterior bayesiano como P(sucesso).

    f* = (p×b - q) / b
    Aplicamos 1/4 Kelly com caps do sistema John Galt:
      - "high"    → cap 2% (OTM, risco não limitado)
      - "defined" → cap 5% (spread, risco definido, RR > 2:1)

    Args:
        posterior: P(H|evidências) do BayesianUpdater
        ganho:     lucro esperado em múltiplos do capital em risco
        perda:     capital em risco (default 1.0 = 100% do alocado)
        risk_type: "high" ou "defined"

    Returns:
        (kelly_full, kelly_quarter, kelly_capped)
        kelly_capped = min(kelly_quarter, cap_do_sistema)
    """
    cap = 0.02 if risk_type == "high" else 0.05

    p = posterior
    q = 1.0 - p
    b = ganho / perda

    f_star    = max(0.0, (p * b - q) / b)
    f_quarter = f_star / 4.0
    f_capped  = min(f_quarter, cap)

    return round(f_star, 4), round(f_quarter, 4), round(f_capped, 4)


def bayesian_sizing_report(
    updater: BayesianUpdater,
    ganho: float,
    perda: float = 1.0,
    capital: float = 10_000.0,
    risk_type: str = "high",
) -> str:
    """Gera relatório completo de sizing bayesiano."""
    f_full, f_quarter, f_capped = bayesian_kelly(
        updater.posterior, ganho, perda, risk_type
    )
    cap_pct = 0.02 if risk_type == "high" else 0.05

    return (
        f"\n{'─'*50}\n"
        f"  SIZING BAYESIANO\n"
        f"{'─'*50}\n"
        f"  Posterior P(sucesso)  : {updater.posterior:.2%}\n"
        f"  Ganho / Perda ratio   : {ganho:.1f}× / {perda:.1f}×\n"
        f"  Kelly full            : {f_full:.2%} do capital\n"
        f"  Kelly 1/4             : {f_quarter:.2%} do capital\n"
        f"  Cap sistema ({risk_type:<8}): {cap_pct:.0%}\n"
        f"  Sizing final (capped) : {f_capped:.2%} = R$ {capital * f_capped:,.2f}\n"
        f"{'─'*50}"
    )


# ---------------------------------------------------------------------------
# Aplicação 4 — Detector de Regime de Mercado
# ---------------------------------------------------------------------------

class MarketRegime:
    """
    Detector bayesiano de regime com três hipóteses mutuamente exclusivas:
      - TRENDING  : mercado direcional, sinais de continuação têm edge
      - REVERTING : mercado ciclico, sinais contrários têm edge
      - VOLATILE  : mercado errático, vol play preferível a direcional
    """

    REGIMES = ["trending", "reverting", "volatile"]

    def __init__(self):
        # Prior uniforme — sem informação inicial sobre o regime
        self.probs: Dict[str, float] = {r: 1 / 3 for r in self.REGIMES}
        self.history: List[str] = []

    def update(self, signal: str) -> Dict[str, float]:
        """
        Atualiza probabilidades de regime dado um sinal observado.
        Usa REGIME_LIKELIHOODS como P(sinal | regime).
        """
        if signal not in REGIME_LIKELIHOODS:
            return self.probs

        likelihoods = REGIME_LIKELIHOODS[signal]
        unnorm = {
            r: likelihoods.get(r, 0.5) * self.probs[r]
            for r in self.REGIMES
        }
        total = sum(unnorm.values())
        if total == 0:
            return self.probs

        self.probs = {r: round(v / total, 6) for r, v in unnorm.items()}
        self.history.append(signal)
        return self.probs

    @property
    def dominant(self) -> str:
        return max(self.probs, key=self.probs.get)

    @property
    def confidence(self) -> float:
        return max(self.probs.values())

    def strategy_hint(self) -> str:
        regime = self.dominant
        conf = self.confidence
        if conf < 0.45:
            return "Regime incerto — aguardar confirmação ou reduzir sizing"
        hints = {
            "trending":  "Tendência identificada — sinais de continuação preferíveis (Bull Spread, OTM Call/Put)",
            "reverting": "Mercado ciclico — sinais contrários preferíveis (RSI extremo, FNG extremo)",
            "volatile":  "Vol elevada — estruturas de volatilidade preferíveis (Straddle, Iron Condor)",
        }
        return hints[regime]

    def summary(self) -> str:
        lines = ["  REGIME DE MERCADO (Bayesiano)", "  " + "─" * 40]
        for r in sorted(self.REGIMES, key=lambda x: -self.probs[x]):
            bar  = "█" * int(self.probs[r] * 25)
            mark = " ◄" if r == self.dominant else ""
            lines.append(f"  {r:<12} {self.probs[r]:>6.1%}  {bar}{mark}")
        lines += [
            "  " + "─" * 40,
            f"  Sinais usados : {len(self.history)}",
            f"  Confiança     : {self.confidence:.1%}",
            f"  Hint          : {self.strategy_hint()}",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Função de análise integrada — usa os 4 módulos em sequência
# ---------------------------------------------------------------------------

def analyze_bayesian(
    ticker: str,
    signals_b3: List[str],
    ganho: float = 2.0,
    perda: float = 1.0,
    capital: float = 10_000.0,
    prior: float = 0.50,
    risk_type: str = "high",
    library: Optional[Dict] = None,
) -> str:
    """
    Pipeline bayesiano completo para um ticker B3.

    Args:
        ticker:     código do ativo (ex: "COGN3")
        signals_b3: lista de sinais observados (chaves de SIGNALS_B3)
        ganho:      lucro esperado em múltiplos do risco
        perda:      capital em risco (default 1.0)
        capital:    capital total da conta em R$
        prior:      P(sucesso) antes dos sinais (default 0.50)
        risk_type:  "high" (OTM) ou "defined" (spread)
        library:    biblioteca de sinais (default SIGNALS_B3)

    Returns:
        Relatório formatado em texto
    """
    lib = library or SIGNALS_B3

    updater = BayesianUpdater(prior=prior)
    regime  = MarketRegime()

    invalid = [s for s in signals_b3 if s not in lib]
    if invalid:
        raise ValueError(f"Sinais inválidos: {invalid}. Disponíveis: {list(lib.keys())}")

    for signal in signals_b3:
        updater.update_from_library(signal, lib)
        regime.update(signal)

    sizing = bayesian_sizing_report(updater, ganho, perda, capital, risk_type)

    # Sinal agregado final
    p = updater.posterior
    if p >= 0.65:
        verdict = "✅ FORTE — edge bayesiano positivo, sizing liberado"
    elif p >= 0.55:
        verdict = "🟡 MODERADO — edge presente, sizing conservador"
    elif p >= 0.45:
        verdict = "⚪ NEUTRO — sem edge claro, evitar posição direcional"
    else:
        verdict = "🔴 NEGATIVO — probabilidade desfavorável, não operar"

    return (
        f"\n{'═'*60}\n"
        f"  ANÁLISE BAYESIANA — {ticker.upper()}\n"
        f"{'═'*60}\n\n"
        f"{updater.summary()}\n\n"
        f"{regime.summary()}\n"
        f"{sizing}\n\n"
        f"  VEREDICTO: {verdict}\n"
        f"{'═'*60}\n"
    )


# ---------------------------------------------------------------------------
# CLI standalone
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    ticker = sys.argv[1].upper() if len(sys.argv) > 1 else "EXEMPLO"

    # --- Aplicação 1: sinal único ---
    print("\n[Aplicação 1] — Sinal único: MM20 breakup")
    u = BayesianUpdater(prior=0.50)
    p = u.update(*SIGNALS_B3["mm20_breakup"], name="mm20_breakup")
    print(f"  Prior: 50.00%  →  Posterior: {p:.2%}")

    # --- Aplicação 2: atualização sequencial ---
    print("\n[Aplicação 2] — Atualização sequencial")
    u2 = BayesianUpdater(prior=0.50)
    for sig in ["mm20_breakup", "volume_spike", "macd_crossover_up", "ibov_positive"]:
        u2.update_from_library(sig, SIGNALS_B3)
    print(u2.summary())

    # --- Aplicação 3: Bayes + Kelly ---
    print("\n[Aplicação 3] — Bayes + Kelly")
    u3 = BayesianUpdater(prior=0.50)
    for sig in ["mm20_breakup", "volume_spike", "rsi_oversold"]:
        u3.update_from_library(sig, SIGNALS_B3)
    print(bayesian_sizing_report(u3, ganho=2.0, perda=1.0, capital=10_000.0, risk_type="defined"))

    # --- Aplicação 4: Regime detector ---
    print("\n[Aplicação 4] — Detector de regime")
    r = MarketRegime()
    for sig in ["mm20_breakup", "volume_spike", "macd_crossover_up"]:
        r.update(sig)
    print(r.summary())

    # --- Pipeline completo ---
    print("\n[Pipeline completo]")
    print(analyze_bayesian(
        ticker=ticker,
        signals_b3=["mm20_breakup", "volume_spike", "macd_crossover_up", "ibov_positive"],
        ganho=2.0,
        perda=1.0,
        capital=10_000.0,
        risk_type="defined",
    ))
