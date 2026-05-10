#!/usr/bin/env python3
"""
Validação de Estratégias via Backtesting - B3
Uso: python3 validate_strategy_backtest.py TICKER [período_dias]
Exemplo: python3 validate_strategy_backtest.py PETR4 365
"""

import sys
import os
import json
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

# Usa o pacote local b3_trading_signals incluído no repositório
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'b3_trading_signals'))

from core.indicator import Indicator
from core.backtester import Backtester
from core.strategies import Strategies

def main():
    # Parse argumentos
    if len(sys.argv) < 2:
        print("❌ Uso: python3 validate_strategy_backtest.py TICKER [dias]")
        print("   Exemplo: python3 validate_strategy_backtest.py PETR4 365")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    if not ticker.endswith('.SA'):
        ticker_full = f"{ticker}.SA"
    else:
        ticker_full = ticker
        ticker = ticker.replace('.SA', '')
    
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
    
    print(f"\n{'='*80}")
    print(f"📊 BACKTESTING - {ticker} (B3)")
    print(f"{'='*80}\n")
    
    # Download dados
    print(f"🔍 Baixando {days} dias de dados históricos...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    df = yf.download(ticker_full, start=start_date, end=end_date, progress=False)
    
    # Flatten MultiIndex columns if necessary
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    if df.empty:
        print(f"❌ Nenhum dado encontrado para {ticker}")
        sys.exit(1)
    
    print(f"✅ {len(df)} dias de dados coletados")
    print(f"📅 Período: {df.index[0].date()} até {df.index[-1].date()}\n")
    
    # Preço atual
    current_price = float(df['Close'].iloc[-1])
    print(f"💰 Preço atual: R$ {current_price:.2f}\n")
    
    # Definir estratégias para testar
    strategies_to_test = [
        # Médias Móveis Simples
        {"ind_t": "SMA", "ind_p": [9, 21]},
        {"ind_t": "SMA", "ind_p": [21, 50]},
        {"ind_t": "SMA", "ind_p": [9, 21, 50]},
        
        # Médias Móveis Exponenciais
        {"ind_t": "EMA", "ind_p": [9, 21]},
        {"ind_t": "EMA", "ind_p": [12, 26]},
        
        # Bollinger Bands
        {"ind_t": "BB", "ind_p": [20, 2]},
        
        # MACD
        {"ind_t": "MACD", "ind_p": [12, 26, 9]},
    ]
    
    print(f"{'='*80}")
    print(f"🔬 TESTANDO {len(strategies_to_test)} ESTRATÉGIAS")
    print(f"{'='*80}\n")
    
    results = []
    
    for i, strategy in enumerate(strategies_to_test, 1):
        ind_t = strategy["ind_t"]
        ind_p = strategy["ind_p"]
        
        # Gerar indicadores
        indicator = Indicator(strategy)
        df_with_ind = indicator.setup_indicator(df.copy())
        
        # Rodar backtest
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        backtester = Backtester(df_with_ind, file_config=config_file)
        try:
            df_result = backtester.run_strategy(strategy)
            
            # Calcular métricas manualmente
            final_return = df_result['Cumulative_Strategy'].iloc[-1]
            total_return = (final_return - 1) * 100
            
            num_trades = int(df_result['Cumulative_Trades'].iloc[-1])
            
            # Sharpe Ratio (simplificado: return / vol)
            strategy_returns = df_result['Strategy']
            if strategy_returns.std() > 0:
                sharpe = (strategy_returns.mean() / strategy_returns.std()) * (252 ** 0.5)  # Anualizado
            else:
                sharpe = 0
            
            # Max Drawdown
            max_drawdown = df_result['Drawdown'].min() * 100
            
            # Win Rate
            trades_df = df_result[df_result['Trade'] == 1].copy()
            if len(trades_df) > 0:
                # Aproximação: trades com retorno positivo
                winning_trades = len(df_result[(df_result['Trade'] == 1) & (df_result['Strategy'] > 0)])
                win_rate = (winning_trades / num_trades * 100) if num_trades > 0 else 0
            else:
                win_rate = 0
            
            # Retorno médio por trade
            avg_trade = (total_return / num_trades) if num_trades > 0 else 0
            
            # Nome da estratégia
            if ind_t in ["SMA", "EMA", "WMA"]:
                if len(ind_p) == 2:
                    strategy_name = f"{ind_t}_{ind_p[0]}_{ind_p[1]}"
                elif len(ind_p) == 3:
                    strategy_name = f"{ind_t}_{ind_p[0]}_{ind_p[1]}_{ind_p[2]}"
                else:
                    strategy_name = f"{ind_t}_{ind_p[0]}"
            elif ind_t == "BB":
                strategy_name = f"BB_{ind_p[0]}_{ind_p[1]}"
            elif ind_t == "MACD":
                strategy_name = f"MACD_{ind_p[0]}_{ind_p[1]}_{ind_p[2]}"
            else:
                strategy_name = ind_t
            
            print(f"[{i}/{len(strategies_to_test)}] {strategy_name:20s} | "
                  f"Retorno: {total_return:+7.2f}% | "
                  f"Sharpe: {sharpe:6.2f} | "
                  f"DD: {max_drawdown:6.2f}% | "
                  f"Trades: {num_trades:3d} | "
                  f"Win%: {win_rate:5.1f}%")
            
            results.append({
                "strategy": strategy_name,
                "ind_t": ind_t,
                "ind_p": ind_p,
                "total_return_pct": round(total_return, 2),
                "sharpe_ratio": round(sharpe, 2),
                "max_drawdown_pct": round(max_drawdown, 2),
                "num_trades": num_trades,
                "win_rate_pct": round(win_rate, 1),
                "avg_trade_pct": round(avg_trade, 2),
            })
            
        except Exception as e:
            print(f"[{i}/{len(strategies_to_test)}] {ind_t:20s} | ❌ ERRO: {str(e)}")
    
    print(f"\n{'='*80}")
    print(f"🏆 RANKING DAS ESTRATÉGIAS")
    print(f"{'='*80}\n")
    
    # Ordenar por retorno total
    results_sorted = sorted(results, key=lambda x: x['total_return_pct'], reverse=True)
    
    print(f"{'Rank':<6} {'Estratégia':<20} {'Retorno':<10} {'Sharpe':<8} {'DD':<8} {'Trades':<8} {'Win%':<8}")
    print(f"{'-'*80}")
    
    for rank, result in enumerate(results_sorted, 1):
        emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"{emoji} {rank:<3} {result['strategy']:<20} "
              f"{result['total_return_pct']:+7.2f}%  "
              f"{result['sharpe_ratio']:6.2f}  "
              f"{result['max_drawdown_pct']:6.2f}%  "
              f"{result['num_trades']:3d}     "
              f"{result['win_rate_pct']:5.1f}%")
    
    # Melhor estratégia
    best = results_sorted[0]
    
    print(f"\n{'='*80}")
    print(f"✅ MELHOR ESTRATÉGIA: {best['strategy']}")
    print(f"{'='*80}")
    print(f"📊 Retorno Total: {best['total_return_pct']:+.2f}%")
    print(f"📈 Sharpe Ratio: {best['sharpe_ratio']:.2f}")
    print(f"📉 Max Drawdown: {best['max_drawdown_pct']:.2f}%")
    print(f"🔄 Número de Trades: {best['num_trades']}")
    print(f"🎯 Taxa de Acerto: {best['win_rate_pct']:.1f}%")
    print(f"💹 Retorno Médio por Trade: {best['avg_trade_pct']:+.2f}%")
    print(f"\n{'='*80}\n")
    
    # Salvar JSON
    output = {
        "ticker": ticker,
        "analysis_date": datetime.now().isoformat(),
        "period_days": days,
        "current_price": round(current_price, 2),
        "strategies_tested": len(strategies_to_test),
        "best_strategy": best,
        "all_results": results_sorted
    }
    
    output_file = f"/tmp/backtest_{ticker}_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultados salvos em: {output_file}\n")

if __name__ == "__main__":
    main()
