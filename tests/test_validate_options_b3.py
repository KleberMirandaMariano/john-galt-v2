"""Testes para validate_options_b3.py"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from validate_options_b3 import OptionsValidatorB3, SELIC_DEFAULT, ATM_THRESHOLD_PCT, KELLY_CONSERVATIVE_DIVISOR


def make_validator(spot=3.27, strike=3.35, days=23, vol=0.65):
    return OptionsValidatorB3(
        ticker="COGN3",
        spot_price=spot,
        strike=strike,
        days_to_expiry=days,
        rf_rate=SELIC_DEFAULT,
        volatility=vol
    )


class TestBlackScholesGreeks:
    def test_delta_call_between_zero_and_one(self):
        v = make_validator()
        greeks = v.calculate_black_scholes_greeks()
        assert greeks is not None
        assert 0 < greeks['delta'] < 1

    def test_pitm_between_zero_and_one(self):
        v = make_validator()
        greeks = v.calculate_black_scholes_greeks()
        assert 0 < greeks['p_itm'] < 1

    def test_theta_always_negative_for_call(self):
        v = make_validator()
        greeks = v.calculate_black_scholes_greeks()
        assert greeks['theta'] < 0, "Theta deve ser negativo para long call"

    def test_gamma_positive(self):
        v = make_validator()
        greeks = v.calculate_black_scholes_greeks()
        assert greeks['gamma'] > 0

    def test_expired_option_returns_none(self):
        v = make_validator(days=0)
        greeks = v.calculate_black_scholes_greeks()
        assert greeks is None
        assert any("expirada" in str(e.get('erro', '')).lower() for e in v.errors)

    def test_deep_itm_delta_near_one(self):
        v = make_validator(spot=5.0, strike=2.0, days=30)
        greeks = v.calculate_black_scholes_greeks()
        assert greeks['delta'] > 0.9

    def test_deep_otm_delta_near_zero(self):
        v = make_validator(spot=2.0, strike=5.0, days=30)
        greeks = v.calculate_black_scholes_greeks()
        assert greeks['delta'] < 0.1


class TestBreakeven:
    def test_breakeven_is_strike_plus_premium(self):
        v = make_validator(strike=3.35)
        be = v.calculate_breakeven(premium=0.085)
        assert abs(be - (3.35 + 0.085)) < 1e-9

    def test_breakeven_not_spot_plus_premium(self):
        v = make_validator(spot=3.27, strike=3.35)
        be = v.calculate_breakeven(premium=0.085)
        wrong = 3.27 + 0.085
        assert be != wrong


class TestMoneyness:
    def test_atm_classification(self):
        v = make_validator(spot=3.27, strike=3.27)
        m = v.classify_moneyness()
        assert m['classification'] == 'ATM'

    def test_itm_classification(self):
        v = make_validator(spot=4.0, strike=3.0)
        m = v.classify_moneyness()
        assert m['classification'] == 'ITM'

    def test_otm_classification(self):
        v = make_validator(spot=2.5, strike=3.5)
        m = v.classify_moneyness()
        assert m['classification'] == 'OTM'

    def test_deep_itm_flag(self):
        v = make_validator(spot=5.0, strike=2.0)
        m = v.classify_moneyness()
        assert m['is_deep'] is True

    def test_near_atm_not_deep(self):
        v = make_validator(spot=3.27, strike=3.30)
        m = v.classify_moneyness()
        assert m['is_deep'] is False


class TestKelly:
    def test_kelly_positive_ev(self):
        v = make_validator()
        k = v.calculate_kelly(p_success=0.6, gain=2.0, loss=1.0)
        assert k['f_star'] > 0

    def test_kelly_conservative_is_quarter(self):
        v = make_validator()
        k = v.calculate_kelly(p_success=0.6, gain=2.0, loss=1.0)
        assert abs(k['f_quarter'] - k['f_star'] / KELLY_CONSERVATIVE_DIVISOR) < 1e-9

    def test_kelly_zero_when_no_edge(self):
        v = make_validator()
        k = v.calculate_kelly(p_success=0.5, gain=1.0, loss=1.0)
        assert k['f_star'] == 0.0

    def test_kelly_zero_loss_returns_zero(self):
        v = make_validator()
        k = v.calculate_kelly(p_success=0.7, gain=2.0, loss=0)
        assert k['f_star'] == 0


class TestPnL:
    def test_pnl_above_strike(self):
        v = make_validator(strike=3.35)
        pnl = v.calculate_pnl(target_price=4.0, premium=0.085, n_contracts=10)
        expected_intrinsic = 4.0 - 3.35
        assert abs(pnl['intrinsic_value'] - expected_intrinsic) < 1e-9
        assert pnl['total_pnl'] > 0

    def test_pnl_below_strike_total_loss(self):
        v = make_validator(strike=3.35)
        pnl = v.calculate_pnl(target_price=2.0, premium=0.085, n_contracts=10)
        assert pnl['intrinsic_value'] == 0
        assert pnl['pnl_per_option'] < 0

    def test_roi_positive_when_profit(self):
        v = make_validator(strike=3.0)
        pnl = v.calculate_pnl(target_price=4.0, premium=0.10, n_contracts=5)
        assert pnl['roi_pct'] > 0


class TestOptionSeries:
    def test_valid_series(self):
        # Formato B3: [TICKER completo][MÊS][STRIKE] — COGN3 + E(mai) + 335
        v = make_validator()
        result = v.validate_option_series("COGN3E335", datetime(2026, 5, 1))
        assert result is not None
        assert result['is_valid'] is True

    def test_wrong_ticker_in_series(self):
        v = make_validator()
        v.validate_option_series("PETR4K100", datetime(2026, 5, 1))
        assert any("difere" in str(e.get('erro', '')).lower() for e in v.errors)

    def test_invalid_month_code(self):
        # 'Z' não é um código de mês B3 válido (A-L)
        v = make_validator()
        v.validate_option_series("COGN3Z335", datetime(2026, 5, 1))
        assert any("mês" in str(e.get('erro', '')).lower() for e in v.errors)
