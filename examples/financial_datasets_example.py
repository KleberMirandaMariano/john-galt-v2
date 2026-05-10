#!/usr/bin/env python3
"""
financial_datasets_example.py - Exemplo de uso para John Galt

Demonstra como usar Financial Datasets API no John Galt
para análise fundamentalista e comparação de ações.

Autor: John Galt v2.0
Data: 10/05/2026
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.financial_datasets import FinancialDatasetsAPI
from src.fundamental_analysis_skill import FundamentalAnalysisSkill
from src.stock_comparison_dashboard import StockComparisonDashboard


def exemplo_1_analise_cogn3():
    """
    Exemplo 1: Análise fundamentalista de COGN3 (Cogna Educação)
    
    Use case: John Galt analisa COGN3 para trade de opções
    """
    print("="*70)
    print("EXEMPLO 1: ANÁLISE FUNDAMENTALISTA COGN3")
    print("="*70)
    print()
    
    skill = FundamentalAnalysisSkill()
    
    # Analisar COGN3
    analysis = skill.analyze("COGN3.SA")
    
    if "error" not in analysis:
        print(f"📊 Ticker: {analysis['ticker']}")
        print()
        
        # Scores
        scores = analysis['scores']
        print("SCORES:")
        print(f"  Value:   {scores['value']:.1f}/10")
        print(f"  Quality: {scores['quality']:.1f}/10")
        print(f"  Growth:  {scores['growth']:.1f}/10")
        print(f"  Risk:    {scores['risk']:.1f}/10")
        print(f"  FINAL:   {scores['final']:.1f}/10")
        print()
        
        # Recomendação
        rec = analysis['recommendation']
        print(f"RECOMENDAÇÃO: {rec['action']}")
        print(f"Confiança: {rec['confidence']*100:.0f}%")
        print(f"Motivo: {rec['rationale']}")
        print()
        
        # Fundamentalistas
        fund = analysis['fundamentals']
        print("FUNDAMENTALISTAS:")
        if fund.get('pe_ratio'):
            print(f"  P/L: {fund['pe_ratio']:.2f}")
        if fund.get('roe'):
            print(f"  ROE: {fund['roe']*100:.1f}%")
        if fund.get('debt_to_equity'):
            print(f"  Dívida/PL: {fund['debt_to_equity']:.2f}")
    else:
        print(f"❌ {analysis['error']}")
        print("(API pode estar indisponível ou sem API key)")
    
    print()


def exemplo_2_comparacao_educacao():
    """
    Exemplo 2: Comparar empresas de educação
    
    Use case: John Galt compara COGN3 vs YDUQ3
    """
    print("="*70)
    print("EXEMPLO 2: COMPARAÇÃO SETOR EDUCAÇÃO")
    print("="*70)
    print()
    
    skill = FundamentalAnalysisSkill()
    
    # Comparar
    tickers = ["COGN3.SA", "YDUQ3.SA"]
    comparison = skill.compare_stocks(tickers)
    
    if comparison.get('ranking'):
        print(f"Ranking ({len(comparison['ranking'])} empresas):")
        print()
        
        for i, ticker in enumerate(comparison['ranking'], 1):
            analysis = next(a for a in comparison['analyses'] if a['ticker'] == ticker)
            score = analysis['scores']['final']
            rec = analysis['recommendation']['action']
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            print(f"{medal} {ticker}: {score:.1f}/10 - {rec}")
        
        print()
        
        # Melhor opção
        if comparison.get('best'):
            best = comparison['best']
            print(f"✅ MELHOR OPÇÃO: {best['ticker']}")
            print(f"   Score: {best['scores']['final']:.1f}/10")
            print(f"   Recomendação: {best['recommendation']['action']}")
    else:
        print("❌ Comparação falhou (API indisponível)")
    
    print()


def exemplo_3_dashboard_petroleo():
    """
    Exemplo 3: Dashboard comparando petrolíferas
    
    Use case: John Galt compara PETR4 vs XOM vs CVX
    """
    print("="*70)
    print("EXEMPLO 3: DASHBOARD SETOR PETRÓLEO")
    print("="*70)
    print()
    
    dashboard = StockComparisonDashboard()
    
    # Gerar dashboard
    tickers = [
        "PETR4.SA",  # Petrobras (B3)
        "XOM",       # Exxon (NYSE)
        "CVX"        # Chevron (NYSE)
    ]
    
    try:
        output_path = "/tmp/petroleo_comparison.html"
        path = dashboard.generate_dashboard(
            tickers=tickers,
            output_path=output_path
        )
        
        print(f"✅ Dashboard gerado: {path}")
        print()
        print("Abra no navegador para ver:")
        print(f"  file://{output_path}")
        print()
        print("Features:")
        print("  📊 Radar chart comparando scores")
        print("  🏆 Ranking automático")
        print("  📋 Tabela de fundamentalistas")
        print("  🎨 Dark theme design")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()


def exemplo_4_telegram_integration():
    """
    Exemplo 4: Como integrar com Telegram do John Galt
    
    Use case: Comandos Telegram para análise fundamentalista
    """
    print("="*70)
    print("EXEMPLO 4: INTEGRAÇÃO TELEGRAM")
    print("="*70)
    print()
    
    print("Comandos sugeridos para SOUL.md:")
    print()
    print("```")
    print(".analise_fundamental <TICKER>")
    print("  Exemplo: .analise_fundamental COGN3")
    print("  Retorna: Análise completa com scores e recomendação")
    print()
    print(".comparar <TICKER1> <TICKER2> ...")
    print("  Exemplo: .comparar PETR4 XOM CVX")
    print("  Retorna: Ranking comparativo")
    print()
    print(".dashboard <SETOR>")
    print("  Exemplo: .dashboard TECH")
    print("  Retorna: Dashboard HTML interativo")
    print("```")
    print()
    
    print("Implementação no bot Telegram:")
    print()
    print("```python")
    print("from src.fundamental_analysis_skill import FundamentalAnalysisSkill")
    print()
    print("skill = FundamentalAnalysisSkill()")
    print()
    print("if command == '.analise_fundamental':")
    print("    ticker = args[0]")
    print("    analysis = skill.analyze(ticker)")
    print("    formatted = skill.format_analysis(analysis)")
    print("    send_telegram_message(formatted)")
    print("```")
    print()


def main():
    """Executar todos os exemplos"""
    print()
    print("🚀 FINANCIAL DATASETS - EXEMPLOS DE USO")
    print()
    
    # Exemplo 1
    exemplo_1_analise_cogn3()
    
    # Exemplo 2
    exemplo_2_comparacao_educacao()
    
    # Exemplo 3
    exemplo_3_dashboard_petroleo()
    
    # Exemplo 4
    exemplo_4_telegram_integration()
    
    print("="*70)
    print("✅ EXEMPLOS CONCLUÍDOS")
    print("="*70)
    print()
    print("Próximos passos:")
    print("1. Configure API key (opcional): export FINANCIAL_DATASETS_API_KEY='...'")
    print("2. Integre com John Galt Telegram bot")
    print("3. Adicione ao daily_report.py")
    print()


if __name__ == "__main__":
    main()
