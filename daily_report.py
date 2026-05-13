#!/usr/bin/env python3
"""
daily_report.py — Relatório Diário John Galt com Financial Datasets

Gera relatório diário combinando:
- Ações B3 (BRAPI)
- Cripto (CoinGecko)
- Opções cripto (OKX)
- Fundamentalistas globais (Financial Datasets) ← NOVO!

Autor: John Galt v2.0 - Daily Report with Financial Datasets
Data: 10/05/2026
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import json

# financial_datasets.py e fundamental_analysis_skill.py estão na mesma pasta
sys.path.insert(0, str(Path(__file__).parent))

from financial_datasets import FinancialDatasetsAPI
from fundamental_analysis_skill import FundamentalAnalysisSkill


# ============================================================================
# CONFIGURATION
# ============================================================================

# Financial Datasets API só suporta NYSE/NASDAQ — B3 não é suportada
# Usando ações globais com liquidez para demonstração do scoring
GLOBAL_TICKERS = [
    "VALE",   # Vale ADR (NYSE)
    "PBR",    # Petrobras ADR (NYSE)
    "ITUB",   # Itaú ADR (NYSE)
    "BBD",    # Bradesco ADR (NYSE)
    "AAPL",   # Apple
    "MSFT",   # Microsoft
]

# Para análise B3 via BRAPI, usar analyze_ticker.py separadamente
B3_TICKERS_BRAPI = ["PETR4", "VALE3", "ITUB4", "BBDC4", "COGN3", "GMAT3"]

CRYPTO_SYMBOLS = ["BTC", "ETH", "SOL"]

# Output acessível via file_read pelo John Galt
OUTPUT_DIR = Path("/root/.zeroclaw/workspace")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# FINANCIAL DATASETS INTEGRATION
# ============================================================================

def get_fundamentals_section() -> str:
    """
    Seção NOVA: Análise fundamentalista via Financial Datasets
    
    Returns:
        Markdown formatado com análise das ações B3
    """
    api = FinancialDatasetsAPI()
    skill = FundamentalAnalysisSkill()
    
    lines = []
    lines.append("# 📊 ANÁLISE FUNDAMENTALISTA (Financial Datasets)")
    lines.append("")
    lines.append(f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append("")
    lines.append("*Nota: Financial Datasets API suporta apenas NYSE/NASDAQ. Para B3, use `analyze_ticker.py`.*")
    lines.append("")

    # Analisar tickers via Financial Datasets
    analyses = []
    
    for ticker in GLOBAL_TICKERS:
        try:
            analysis = skill.analyze(ticker)

            if "error" not in analysis:
                analyses.append(analysis)
        except Exception as e:
            print(f"⚠️ Erro ao analisar {ticker}: {e}")
    
    if not analyses:
        lines.append("⚠️ **Nenhuma análise disponível** (API pode estar indisponível)")
        lines.append("")
        return "\n".join(lines)
    
    # Ordenar por score final
    analyses.sort(key=lambda x: x['scores']['final'], reverse=True)
    
    # Ranking
    lines.append("## 🏆 Ranking por Score Final")
    lines.append("")
    
    for i, analysis in enumerate(analyses, 1):
        ticker = analysis['ticker']
        score = analysis['scores']['final']
        rec = analysis['recommendation']['action']
        
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        emoji_score = "🟢" if score >= 7.5 else "🟡" if score >= 5.5 else "🔴"
        
        lines.append(f"{medal} **{ticker}**: {score:.1f}/10 {emoji_score} — {rec}")
    
    lines.append("")
    
    # Detalhes das Top 3
    lines.append("## 📈 Top 3 — Análise Detalhada")
    lines.append("")
    
    for analysis in analyses[:3]:
        ticker = analysis['ticker']
        scores = analysis['scores']
        rec = analysis['recommendation']
        fund = analysis['fundamentals']
        
        lines.append(f"### {ticker}")
        lines.append("")
        
        # Scores
        lines.append("**Scores:**")
        lines.append(f"- Value: {scores['value']:.1f}/10")
        lines.append(f"- Quality: {scores['quality']:.1f}/10")
        lines.append(f"- Growth: {scores['growth']:.1f}/10")
        lines.append(f"- Risk: {scores['risk']:.1f}/10")
        lines.append(f"- **FINAL: {scores['final']:.1f}/10**")
        lines.append("")
        
        # Recomendação
        lines.append("**Recomendação:**")
        lines.append(f"- Ação: **{rec['action']}**")
        lines.append(f"- Confiança: {rec['confidence']*100:.0f}%")
        lines.append(f"- Motivo: {rec['rationale']}")
        lines.append("")
        
        # Fundamentalistas chave
        lines.append("**Fundamentalistas:**")
        if fund.get('pe_ratio'):
            lines.append(f"- P/L: {fund['pe_ratio']:.2f}")
        if fund.get('pb_ratio'):
            lines.append(f"- P/VP: {fund['pb_ratio']:.2f}")
        if fund.get('roe'):
            lines.append(f"- ROE: {fund['roe']*100:.1f}%")
        if fund.get('debt_to_equity'):
            lines.append(f"- Dívida/PL: {fund['debt_to_equity']:.2f}")
        if fund.get('revenue_growth'):
            lines.append(f"- Cresc. Receita: {fund['revenue_growth']*100:+.1f}%")
        if fund.get('dividend_yield'):
            lines.append(f"- Dividend Yield: {fund['dividend_yield']*100:.1f}%")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def get_value_opportunities() -> str:
    """
    Seção: Oportunidades de Value Investing
    
    Returns:
        Markdown com ações undervalued
    """
    skill = FundamentalAnalysisSkill()
    
    lines = []
    lines.append("# 💎 OPORTUNIDADES VALUE INVESTING")
    lines.append("")
    
    # Analisar tickers
    undervalued = []
    
    for ticker in GLOBAL_TICKERS:
        try:
            analysis = skill.analyze(ticker)

            if "error" not in analysis:
                # Value score >= 7.0 = undervalued
                if analysis['scores']['value'] >= 7.0:
                    undervalued.append(analysis)
        except Exception as e:
            continue
    
    if not undervalued:
        lines.append("⚠️ **Nenhuma oportunidade de value encontrada**")
        lines.append("(Critério: Value score >= 7.0/10)")
        lines.append("")
        return "\n".join(lines)
    
    # Ordenar por value score
    undervalued.sort(key=lambda x: x['scores']['value'], reverse=True)
    
    lines.append(f"**Encontradas {len(undervalued)} oportunidades:**")
    lines.append("")
    
    for analysis in undervalued:
        ticker = analysis['ticker']
        value_score = analysis['scores']['value']
        fund = analysis['fundamentals']
        
        lines.append(f"### {ticker} — Value Score: {value_score:.1f}/10 🟢")
        lines.append("")
        
        # Métricas value
        lines.append("**Valuation:**")
        if fund.get('pe_ratio'):
            status = "✅ Atrativo" if fund['pe_ratio'] < 15 else "⚠️ Caro"
            lines.append(f"- P/L: {fund['pe_ratio']:.2f} {status}")
        
        if fund.get('pb_ratio'):
            status = "✅ Barato" if fund['pb_ratio'] < 1.0 else "✅ Razoável" if fund['pb_ratio'] < 3.0 else "⚠️ Caro"
            lines.append(f"- P/VP: {fund['pb_ratio']:.2f} {status}")
        
        if fund.get('dividend_yield'):
            status = "✅ Alto" if fund['dividend_yield'] > 0.05 else "✅ Bom" if fund['dividend_yield'] > 0.03 else ""
            lines.append(f"- Dividend Yield: {fund['dividend_yield']*100:.1f}% {status}")
        
        lines.append("")
        
        # Recomendação
        rec = analysis['recommendation']
        lines.append(f"**Recomendação:** {rec['action']} ({rec['confidence']*100:.0f}% confiança)")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def get_quality_leaders() -> str:
    """
    Seção: Empresas de Alta Qualidade
    
    Returns:
        Markdown com empresas quality score alto
    """
    skill = FundamentalAnalysisSkill()
    
    lines = []
    lines.append("# ⭐ LÍDERES EM QUALIDADE")
    lines.append("")
    
    # Analisar tickers
    quality_leaders = []
    
    for ticker in GLOBAL_TICKERS:
        try:
            analysis = skill.analyze(ticker)

            if "error" not in analysis:
                # Quality score >= 7.0
                if analysis['scores']['quality'] >= 7.0:
                    quality_leaders.append(analysis)
        except Exception as e:
            continue
    
    if not quality_leaders:
        lines.append("⚠️ **Nenhuma empresa de alta qualidade encontrada**")
        lines.append("(Critério: Quality score >= 7.0/10)")
        lines.append("")
        return "\n".join(lines)
    
    # Ordenar por quality score
    quality_leaders.sort(key=lambda x: x['scores']['quality'], reverse=True)
    
    lines.append(f"**Encontradas {len(quality_leaders)} empresas:**")
    lines.append("")
    
    for analysis in quality_leaders:
        ticker = analysis['ticker']
        quality_score = analysis['scores']['quality']
        fund = analysis['fundamentals']
        
        lines.append(f"### {ticker} — Quality Score: {quality_score:.1f}/10 ⭐")
        lines.append("")
        
        # Métricas quality
        lines.append("**Rentabilidade:**")
        if fund.get('roe'):
            status = "🟢 Excelente" if fund['roe'] > 0.20 else "🟢 Boa" if fund['roe'] > 0.15 else ""
            lines.append(f"- ROE: {fund['roe']*100:.1f}% {status}")
        
        if fund.get('roa'):
            status = "🟢 Excelente" if fund['roa'] > 0.10 else "🟢 Boa" if fund['roa'] > 0.05 else ""
            lines.append(f"- ROA: {fund['roa']*100:.1f}% {status}")
        
        if fund.get('net_margin'):
            status = "🟢 Alta" if fund['net_margin'] > 0.15 else "🟢 Boa" if fund['net_margin'] > 0.10 else ""
            lines.append(f"- Margem Líquida: {fund['net_margin']*100:.1f}% {status}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


# ============================================================================
# CRYPTO SECTION (placeholder - já existe em cripto_daily.sh)
# ============================================================================

def get_crypto_section() -> str:
    """
    Seção de cripto (placeholder)
    
    Na prática, usar CoinGecko + OKX como já implementado
    """
    lines = []
    lines.append("# 💰 CRIPTOMOEDAS")
    lines.append("")
    lines.append("(Ver relatório cripto separado via `cripto_daily.sh`)")
    lines.append("")
    
    return "\n".join(lines)


# ============================================================================
# MAIN REPORT GENERATOR
# ============================================================================

def generate_daily_report() -> str:
    """
    Gerar relatório diário completo
    
    Returns:
        Markdown formatado
    """
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    report = f"""# 📊 RELATÓRIO DIÁRIO — JOHN GALT v2.0

**Data:** {timestamp}

**Cobertura:**
- ADRs B3 + Globais (NYSE/NASDAQ): {len(GLOBAL_TICKERS)} tickers
- Análise Fundamentalista: Financial Datasets API
- Scoring System: Value/Quality/Growth/Risk
- B3 direto: use `analyze_ticker.py TICKER` + `file_read`

---

"""
    
    # Seção 1: Análise Fundamentalista
    report += get_fundamentals_section()
    report += "\n\n"
    
    # Seção 2: Oportunidades Value
    report += get_value_opportunities()
    report += "\n\n"
    
    # Seção 3: Líderes Quality
    report += get_quality_leaders()
    report += "\n\n"
    
    # Seção 4: Cripto (placeholder)
    report += get_crypto_section()
    report += "\n\n"
    
    # Footer
    report += """---

**Gerado por:** John Galt v2.0 - Financial Datasets Integration
**Próximo relatório:** Amanhã às 09:00 BRT

---

*Disclaimer: Este relatório é apenas informativo. Não constitui recomendação de investimento.*
"""
    
    return report


def save_report(report: str, output_path: Path = None) -> Path:
    """
    Salvar relatório em arquivo
    
    Args:
        report: Conteúdo do relatório
        output_path: Caminho customizado (opcional)
    
    Returns:
        Path do arquivo salvo
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = OUTPUT_DIR / f"daily_report_{timestamp}.md"
        # John Galt lê com: file_read /root/.zeroclaw/workspace/daily_report_{timestamp}.md
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return output_path


def send_telegram(report: str):
    """
    Enviar relatório via Telegram
    
    Token e chat_id via variáveis de ambiente ou hardcoded como fallback.
    Divide mensagens longas automaticamente (limite Telegram: 4096 chars).
    """
    import requests as _requests

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8930603673:AAHHbMpUnsNq5KaAcJNsuuvZ1nSaeARHaP0")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1808474055")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Dividir em chunks de 4096 chars (limite do Telegram)
    MAX_LEN = 4096
    chunks = [report[i:i+MAX_LEN] for i in range(0, len(report), MAX_LEN)]
    
    success = True
    for i, chunk in enumerate(chunks, 1):
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown"
        }
        try:
            resp = _requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                print(f"   ✅ Chunk {i}/{len(chunks)} enviado")
            else:
                # Tentar sem Markdown se der erro de parse
                payload["parse_mode"] = ""
                resp2 = _requests.post(url, json=payload, timeout=15)
                if resp2.status_code == 200:
                    print(f"   ✅ Chunk {i}/{len(chunks)} enviado (sem markdown)")
                else:
                    print(f"   ❌ Erro chunk {i}: {resp2.text[:100]}")
                    success = False
        except Exception as e:
            print(f"   ❌ Exceção ao enviar chunk {i}: {e}")
            success = False
    
    if success:
        print(f"📱 Telegram: ✅ Relatório enviado ({len(chunks)} parte(s))")
    else:
        print("📱 Telegram: ⚠️ Alguns chunks falharam")


def send_email(report: str):
    """
    Enviar relatório via Email (placeholder)
    
    TODO: Integrar com Gmail API
    """
    print("📧 TODO: Implementar envio Email")
    print(f"   Tamanho do relatório: {len(report)} chars")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Executar geração do relatório diário"""
    print("="*70)
    print("📊 JOHN GALT - DAILY REPORT GENERATOR")
    print("="*70)
    print()
    
    print(f"🕐 Gerando relatório: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    
    # Gerar relatório
    print("1️⃣ Gerando seção de análise fundamentalista...")
    report = generate_daily_report()
    
    # Salvar
    print("2️⃣ Salvando relatório...")
    output_path = save_report(report)
    print(f"   ✅ Salvo em: {output_path}")
    print()
    
    # Enviar (placeholder)
    print("3️⃣ Enviando relatório...")
    send_telegram(report)
    send_email(report)
    print()
    
    print("="*70)
    print("✅ RELATÓRIO DIÁRIO GERADO COM SUCESSO!")
    print("="*70)
    print()
    
    # Mostrar preview
    print("PREVIEW:")
    print("-"*70)
    lines = report.split('\n')
    for line in lines[:30]:  # Primeiras 30 linhas
        print(line)
    print(f"\n... ({len(lines)} linhas totais)")
    print()


if __name__ == "__main__":
    main()
