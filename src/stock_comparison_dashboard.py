#!/usr/bin/env python3
"""
stock_comparison_dashboard.py - Dashboard de Comparação de Ações

Gera dashboard HTML interativo comparando múltiplas ações
Usa Financial Datasets API + Fundamental Analysis Skill

Autor: John Galt v2.0 - Stock Comparison Dashboard
Data: 08/05/2026
"""

from typing import List, Dict
from src.financial_datasets import FinancialDatasetsAPI
from src.fundamental_analysis_skill import FundamentalAnalysisSkill
import json


class StockComparisonDashboard:
    """
    Dashboard HTML interativo para comparação de ações
    
    Features:
    - Comparação lado-a-lado
    - Gráficos de radar
    - Tabela de fundamentalistas
    - Ranking automático
    """
    
    def __init__(self):
        self.api = FinancialDatasetsAPI()
        self.skill = FundamentalAnalysisSkill()
    
    def generate_dashboard(
        self, 
        tickers: List[str],
        output_path: str = "/mnt/user-data/outputs/stock_comparison.html"
    ) -> str:
        """
        Gerar dashboard HTML
        
        Args:
            tickers: Lista de tickers para comparar
            output_path: Caminho do arquivo HTML
        
        Returns:
            Path do arquivo gerado
        """
        # Obter dados
        comparison = self.skill.compare_stocks(tickers)
        
        # Gerar HTML
        html = self._generate_html(comparison)
        
        # Salvar
        with open(output_path, 'w') as f:
            f.write(html)
        
        return output_path
    
    def _generate_html(self, comparison: Dict) -> str:
        """Gerar HTML completo"""
        tickers = comparison['tickers']
        analyses = comparison['analyses']
        
        # Preparar dados para gráficos
        chart_data = self._prepare_chart_data(analyses)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Comparison Dashboard - John Galt</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            color: #fff;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #00f260, #0575e6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .subtitle {{
            color: #a0a0a0;
            font-size: 1.1em;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .card h2 {{
            margin-bottom: 20px;
            font-size: 1.5em;
            color: #00f260;
        }}
        
        .stock-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid;
        }}
        
        .rank-1 {{ border-left-color: #FFD700; }}
        .rank-2 {{ border-left-color: #C0C0C0; }}
        .rank-3 {{ border-left-color: #CD7F32; }}
        .rank-other {{ border-left-color: #555; }}
        
        .stock-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .ticker {{
            font-size: 1.8em;
            font-weight: bold;
        }}
        
        .score {{
            font-size: 2em;
            font-weight: bold;
        }}
        
        .score.high {{ color: #00f260; }}
        .score.medium {{ color: #ffd700; }}
        .score.low {{ color: #ff6b6b; }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }}
        
        .metric {{
            background: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 8px;
        }}
        
        .metric-label {{
            color: #a0a0a0;
            font-size: 0.85em;
            margin-bottom: 5px;
        }}
        
        .metric-value {{
            font-size: 1.2em;
            font-weight: bold;
        }}
        
        .recommendation {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        
        .rec-strong-buy {{ background: linear-gradient(90deg, #00f260, #0575e6); }}
        .rec-buy {{ background: #00f260; color: #000; }}
        .rec-hold {{ background: #ffd700; color: #000; }}
        .rec-sell {{ background: #ff6b6b; }}
        .rec-strong-sell {{ background: #dc143c; }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin-top: 20px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        th {{
            background: rgba(0, 242, 96, 0.1);
            font-weight: bold;
            color: #00f260;
        }}
        
        tr:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .badge-high {{ background: #00f260; color: #000; }}
        .badge-medium {{ background: #ffd700; color: #000; }}
        .badge-low {{ background: #ff6b6b; }}
        
        footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: #a0a0a0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Stock Comparison Dashboard</h1>
            <p class="subtitle">Powered by John Galt v2.0 + Financial Datasets API</p>
        </header>
        
        <!-- Ranking Section -->
        <div class="card">
            <h2>🏆 Ranking por Score Final</h2>
            {self._generate_ranking_html(analyses)}
        </div>
        
        <!-- Radar Chart -->
        <div class="card">
            <h2>📈 Comparação de Scores</h2>
            <div class="chart-container">
                <canvas id="radarChart"></canvas>
            </div>
        </div>
        
        <!-- Fundamentals Table -->
        <div class="card">
            <h2>📋 Fundamentalistas Detalhados</h2>
            {self._generate_table_html(analyses)}
        </div>
    </div>
    
    <footer>
        <p>Generated by John Galt v2.0 | Data: Financial Datasets API</p>
        <p>{self._get_timestamp()}</p>
    </footer>
    
    <script>
        // Radar Chart
        const ctx = document.getElementById('radarChart').getContext('2d');
        const radarChart = new Chart(ctx, {{
            type: 'radar',
            data: {json.dumps(chart_data)},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 10,
                        ticks: {{
                            color: '#fff',
                            backdropColor: 'transparent'
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }},
                        pointLabels: {{
                            color: '#00f260',
                            font: {{
                                size: 14,
                                weight: 'bold'
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        labels: {{
                            color: '#fff',
                            font: {{
                                size: 14
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        return html
    
    def _generate_ranking_html(self, analyses: List[Dict]) -> str:
        """Gerar HTML do ranking"""
        html_parts = []
        
        for i, analysis in enumerate(analyses, 1):
            ticker = analysis['ticker']
            score = analysis['scores']['final']
            rec = analysis['recommendation']
            
            rank_class = f"rank-{i}" if i <= 3 else "rank-other"
            score_class = "high" if score >= 7.5 else "medium" if score >= 5.5 else "low"
            rec_class = f"rec-{rec['action'].lower().replace('_', '-')}"
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            html_parts.append(f"""
            <div class="stock-card {rank_class}">
                <div class="stock-header">
                    <div>
                        <span style="font-size: 1.5em; margin-right: 10px;">{medal}</span>
                        <span class="ticker">{ticker}</span>
                    </div>
                    <div class="score {score_class}">{score:.1f}/10</div>
                </div>
                
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-label">Value</div>
                        <div class="metric-value">{analysis['scores']['value']:.1f}/10</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Quality</div>
                        <div class="metric-value">{analysis['scores']['quality']:.1f}/10</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Growth</div>
                        <div class="metric-value">{analysis['scores']['growth']:.1f}/10</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Risk</div>
                        <div class="metric-value">{analysis['scores']['risk']:.1f}/10</div>
                    </div>
                </div>
                
                <div class="recommendation {rec_class}">
                    {rec['action'].replace('_', ' ')} • {rec['confidence']*100:.0f}% confiança
                </div>
            </div>
            """)
        
        return "\n".join(html_parts)
    
    def _generate_table_html(self, analyses: List[Dict]) -> str:
        """Gerar tabela HTML de fundamentalistas"""
        html = """
        <table>
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>P/L</th>
                    <th>P/VP</th>
                    <th>ROE</th>
                    <th>Dívida/PL</th>
                    <th>Marg. Líq</th>
                    <th>Cresc. Rec</th>
                    <th>Div. Yield</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for analysis in analyses:
            ticker = analysis['ticker']
            fund = analysis['fundamentals']
            
            html += f"""
                <tr>
                    <td><strong>{ticker}</strong></td>
                    <td>{self._format_value(fund.get('pe_ratio'))}</td>
                    <td>{self._format_value(fund.get('pb_ratio'))}</td>
                    <td>{self._format_percent(fund.get('roe'))}</td>
                    <td>{self._format_value(fund.get('debt_to_equity'))}</td>
                    <td>{self._format_percent(fund.get('net_margin'))}</td>
                    <td>{self._format_percent(fund.get('revenue_growth'), show_sign=True)}</td>
                    <td>{self._format_percent(fund.get('dividend_yield'))}</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        """
        
        return html
    
    def _prepare_chart_data(self, analyses: List[Dict]) -> Dict:
        """Preparar dados para Chart.js"""
        datasets = []
        
        colors = [
            'rgba(0, 242, 96, 0.7)',
            'rgba(255, 215, 0, 0.7)',
            'rgba(255, 107, 107, 0.7)',
            'rgba(5, 117, 230, 0.7)',
            'rgba(147, 51, 234, 0.7)'
        ]
        
        for i, analysis in enumerate(analyses):
            color = colors[i % len(colors)]
            
            datasets.append({
                'label': analysis['ticker'],
                'data': [
                    analysis['scores']['value'],
                    analysis['scores']['quality'],
                    analysis['scores']['growth'],
                    analysis['scores']['risk']
                ],
                'backgroundColor': color.replace('0.7', '0.2'),
                'borderColor': color,
                'borderWidth': 2
            })
        
        return {
            'labels': ['Value', 'Quality', 'Growth', 'Risk'],
            'datasets': datasets
        }
    
    def _format_value(self, value) -> str:
        """Formatar valor"""
        if value is None:
            return "N/A"
        return f"{value:.2f}"
    
    def _format_percent(self, value, show_sign: bool = False) -> str:
        """Formatar percentual"""
        if value is None:
            return "N/A"
        
        pct = value * 100
        if show_sign:
            return f"{pct:+.1f}%"
        return f"{pct:.1f}%"
    
    def _get_timestamp(self) -> str:
        """Timestamp formatado"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demonstração do dashboard"""
    print("📊 STOCK COMPARISON DASHBOARD - DEMO")
    print("="*70)
    print()
    
    dashboard = StockComparisonDashboard()
    
    # Gerar dashboard comparando Tech Giants
    print("Gerando dashboard para AAPL, MSFT, GOOGL...")
    output_path = dashboard.generate_dashboard(["AAPL", "MSFT", "GOOGL"])
    
    print(f"✅ Dashboard gerado: {output_path}")
    print()
    print("Abra o arquivo HTML no navegador para visualizar!")
    print()
    print("="*70)


if __name__ == "__main__":
    demo()
