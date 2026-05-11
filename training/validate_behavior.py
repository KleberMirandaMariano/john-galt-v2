#!/usr/bin/env python3
"""
validate_behavior.py — Validador Comportamental do John Galt

Verifica se respostas do John Galt seguem as regras definidas em SOUL.md/AGENTS.md.

Dois modos:
  --check-response  Valida uma resposta já gerada (stdin ou arquivo)
  --run-suite       Envia prompts para a API e valida automaticamente (requer ANTHROPIC_API_KEY)

Uso:
  # Validar resposta existente de um arquivo
  python3 validate_behavior.py --check-response --file resposta.txt --command cripto

  # Rodar suite completa contra a API (precisa das env vars do .env)
  python3 validate_behavior.py --run-suite

  # Listar todos os casos de teste
  python3 validate_behavior.py --list
"""

import os
import sys
import re
import json
import argparse
from dataclasses import dataclass, field
from typing import Optional

# ─── Casos de Teste ──────────────────────────────────────────────────────────

@dataclass
class TestCase:
    id: str
    command: str
    prompt: str
    must_contain: list[str]       # strings que DEVEM aparecer na resposta
    must_not_contain: list[str]   # strings que NÃO DEVEM aparecer
    description: str

TEST_SUITE: list[TestCase] = [
    TestCase(
        id="cripto-01",
        command="cripto",
        prompt="cripto",
        must_contain=[
            "BTC",
            "ETH",
            "SOL",
            "Fear",
            "coingecko",          # deve mencionar a fonte
        ],
        must_not_contain=[
            "python3",
            "shell(",
            "import ",
            "localhost",
            "src.",
            "glob_search",
        ],
        description="Comando .cripto deve buscar CoinGecko + FNG e mostrar BTC/ETH/SOL",
    ),
    TestCase(
        id="cripto-02",
        command="cripto",
        prompt="me dá o preço do bitcoin",
        must_contain=[
            "web_fetch",           # deve invocar web_fetch explicitamente
            "coingecko",
        ],
        must_not_contain=[
            "python3",
            "curl",
            "shell",
        ],
        description="Pergunta informal sobre BTC também deve usar web_fetch CoinGecko",
    ),
    TestCase(
        id="b3-cogn3-01",
        command="analise",
        prompt="analise COGN3",
        must_contain=[
            "brapi",              # deve usar BRAPI para B3
            "regularMarketPrice", # ou ao menos mencionar o campo
            "52",                 # faixa 52 semanas
            "Fear",               # deve buscar Fear & Greed também
            "%",                  # posição na faixa em %
        ],
        must_not_contain=[
            "financialdatasets",  # Financial Datasets não cobre B3
            "python3",
            "shell(",
            "localhost",
            "src.",
        ],
        description="Análise COGN3 deve usar BRAPI (não Financial Datasets) + FNG",
    ),
    TestCase(
        id="b3-cogn3-02",
        command="analise",
        prompt=".analise COGN3",
        must_contain=[
            "R$",                 # preço em BRL
            "P/L",                # múltiplo obrigatório
            "Market Cap",
        ],
        must_not_contain=[
            "python3",
            "shell",
        ],
        description="Formato .analise com ponto também deve funcionar igual",
    ),
    TestCase(
        id="global-aapl-01",
        command="analise",
        prompt="analise AAPL",
        must_contain=[
            "financialdatasets",  # Financial Datasets para NYSE/NASDAQ
            "Value",              # seção de scores
            "Quality",
            "Growth",
            "Risk",
            "Score",
            "BUY",                # ou SELL ou HOLD — deve dar recomendação
        ],
        must_not_contain=[
            "brapi",              # BRAPI não cobre NYSE
            "python3",
            "shell(",
            "localhost",
        ],
        description="Análise AAPL deve usar Financial Datasets com 4 scores (V/Q/G/R)",
    ),
    TestCase(
        id="resumo-01",
        command="resumo",
        prompt="resumo",
        must_contain=[
            "BTC",
            "PETR4",              # deve buscar B3
            "USD",                # câmbio
            "Fear",
        ],
        must_not_contain=[
            "python3",
            "shell(",
        ],
        description="Comando .resumo deve consolidar cripto + B3 + macro",
    ),
    TestCase(
        id="estruturas-sol-01",
        command="estruturas",
        prompt="estruturas SOL",
        must_contain=[
            "VALIDAÇÃO",          # seção obrigatória
            "RISK GATING",        # seção obrigatória
            "SCORES",             # seção obrigatória
            "DECISÃO",            # seção obrigatória
            "Iron Condor",        # ou outra estratégia — deve recomendar UMA
            "Kelly",              # sizing via Kelly
            "Black-Scholes",      # ou d1/d2 calculados inline
            "Delta",              # Greeks obrigatórios
        ],
        must_not_contain=[
            "Cenário 1",          # anti-padrão: 4 cenários paralelos
            "Cenário 2",
            "python3",
            "shell(",
            "localhost",
        ],
        description="Estruturas SOL deve ter 4 seções + UMA estratégia (não 4 cenários)",
    ),
    TestCase(
        id="estruturas-cogn3-01",
        command="estruturas",
        prompt="estratégias de opções para COGN3",
        must_contain=[
            "VALIDAÇÃO",
            "RISK GATING",
            "SCORES",
            "DECISÃO",
            "Selic",              # B3 usa Selic como taxa livre de risco
            "Black-Scholes",
        ],
        must_not_contain=[
            "Cenário 1",
            "Cenário 2",
            "python3",
            "shell(",
            "financialdatasets",  # B3 não usa Financial Datasets
        ],
        description="Estratégias B3 deve usar Selic (BCB) + BRAPI + 4 seções obrigatórias",
    ),
    TestCase(
        id="no-shell-01",
        command="geral",
        prompt="pode rodar o analyze_ticker.py para mim?",
        must_contain=[
            "file_read",          # deve sugerir file_read após usuário rodar manualmente
        ],
        must_not_contain=[
            "python3",
            "shell(",
            "subprocess",
            "os.system",
        ],
        description="Nunca deve tentar rodar scripts via shell — apenas file_read do output",
    ),
    TestCase(
        id="no-memory-01",
        command="geral",
        prompt="qual o IV do Bitcoin hoje?",
        must_contain=[
            "web_fetch",          # deve buscar via web_fetch, não inventar
            "okx",                # OKX tem dados de options
        ],
        must_not_contain=[
            "aproximadamente",    # indício de uso de memória
            "normalmente",
            "historicamente",
            "em torno de",
        ],
        description="IV deve ser buscado via OKX, não inventado com base em memória",
    ),
]

# ─── Validador ────────────────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    test_id: str
    passed: bool
    score: float
    violations: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    details: str = ""

def validate_response(response: str, case: TestCase) -> ValidationResult:
    """Valida uma resposta de texto contra um caso de teste."""
    response_lower = response.lower()

    violations = []
    missing = []

    # Verificar strings proibidas
    for forbidden in case.must_not_contain:
        if forbidden.lower() in response_lower:
            violations.append(f"Contém '{forbidden}' (PROIBIDO)")

    # Verificar strings obrigatórias
    for required in case.must_contain:
        if required.lower() not in response_lower:
            missing.append(f"Falta '{required}' (OBRIGATÓRIO)")

    total_checks = len(case.must_contain) + len(case.must_not_contain)
    passed_checks = (len(case.must_contain) - len(missing)) + (len(case.must_not_contain) - len(violations))
    score = passed_checks / total_checks if total_checks > 0 else 1.0
    passed = len(violations) == 0 and len(missing) == 0

    return ValidationResult(
        test_id=case.id,
        passed=passed,
        score=round(score, 2),
        violations=violations,
        missing=missing,
        details=case.description,
    )

def print_result(result: ValidationResult, case: TestCase) -> None:
    status = "✅ PASSOU" if result.passed else "❌ FALHOU"
    bar = "━" * 55
    print(f"\n{bar}")
    print(f"{status}  [{result.test_id}]  score={result.score:.0%}")
    print(f"  {case.description}")

    if result.violations:
        print(f"\n  🚫 VIOLAÇÕES (proibido encontrado):")
        for v in result.violations:
            print(f"     • {v}")

    if result.missing:
        print(f"\n  ⚠️  AUSÊNCIAS (obrigatório faltando):")
        for m in result.missing:
            print(f"     • {m}")

def print_summary(results: list[ValidationResult]) -> None:
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    avg_score = sum(r.score for r in results) / total if total else 0
    bar = "━" * 55
    overall = "✅ APROVADO" if passed == total else ("⚠️ PARCIAL" if passed > total // 2 else "❌ REPROVADO")

    print(f"\n{'═' * 55}")
    print(f"RESULTADO GERAL: {overall}")
    print(f"Passou: {passed}/{total} casos  |  Score médio: {avg_score:.0%}")
    print(f"{'═' * 55}")

    failed = [r for r in results if not r.passed]
    if failed:
        print(f"\nCasos que falharam:")
        for r in failed:
            print(f"  ❌ [{r.id}] — {r.details[:60]}")

# ─── Modo: run-suite via API ──────────────────────────────────────────────────

def load_system_prompt() -> str:
    """Carrega SOUL.md + AGENTS.md como system prompt."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parts = []
    for fname in ["config/SOUL.md", "config/AGENTS.md", "config/TOOLS.md"]:
        path = os.path.join(base, fname)
        if os.path.exists(path):
            with open(path) as f:
                parts.append(f.read())
    return "\n\n---\n\n".join(parts)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-sonnet-4-5"


def run_suite(
    test_ids: Optional[list[str]] = None,
    model: str = DEFAULT_MODEL,
) -> list[ValidationResult]:
    """Roda a suite completa via OpenRouter e valida cada resposta."""
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai não instalado. Execute: pip install openai")
        sys.exit(1)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY não definida. Configure no .env")
        sys.exit(1)

    client = OpenAI(
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
    )

    system_prompt = load_system_prompt()
    cases = TEST_SUITE if not test_ids else [c for c in TEST_SUITE if c.id in test_ids]

    print(f"Modelo: {model}")
    print(f"Casos: {len(cases)} | Base URL: {OPENROUTER_BASE_URL}")

    results = []
    for case in cases:
        print(f"\n[{case.id}] Enviando: '{case.prompt}' ...")
        try:
            response = client.chat.completions.create(
                model=model,
                max_tokens=2048,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": case.prompt},
                ],
            )
            response_text = response.choices[0].message.content or ""
        except Exception as e:
            print(f"  ⚠️  Erro na API: {e}")
            results.append(ValidationResult(
                test_id=case.id,
                passed=False,
                score=0.0,
                violations=[f"Erro API: {e}"],
                details=case.description,
            ))
            continue

        result = validate_response(response_text, case)
        results.append(result)
        print_result(result, case)

    print_summary(results)
    return results

# ─── Modo: check-response (arquivo ou stdin) ──────────────────────────────────

def check_response_file(filepath: str, command: str) -> None:
    """Valida uma resposta salva em arquivo."""
    if filepath == "-":
        response_text = sys.stdin.read()
    else:
        with open(filepath) as f:
            response_text = f.read()

    cases = [c for c in TEST_SUITE if c.command == command or c.id == command]
    if not cases:
        # fallback: rodar todos os casos do mesmo command group
        cases = [c for c in TEST_SUITE if command in c.id]
    if not cases:
        print(f"❌ Nenhum caso de teste para command='{command}'. Use --list para ver opções.")
        sys.exit(1)

    results = []
    for case in cases:
        result = validate_response(response_text, case)
        results.append(result)
        print_result(result, case)

    print_summary(results)

# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validador comportamental do John Galt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--run-suite",
        action="store_true",
        help="Rodar suite completa via OpenRouter",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Modelo OpenRouter (padrão: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--check-response",
        action="store_true",
        help="Validar resposta de arquivo (--file) ou stdin (-)",
    )
    parser.add_argument(
        "--file",
        default="-",
        help="Arquivo com a resposta a validar (ou - para stdin)",
    )
    parser.add_argument(
        "--command",
        default="geral",
        help="Tipo de comando para selecionar casos: cripto, analise, resumo, estruturas, geral",
    )
    parser.add_argument(
        "--test-ids",
        nargs="+",
        help="IDs específicos de casos para rodar (ex: cripto-01 b3-cogn3-01)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar todos os casos de teste disponíveis",
    )
    parser.add_argument(
        "--output-json",
        help="Salvar resultados em JSON",
    )

    args = parser.parse_args()

    if args.list:
        print(f"\n{'─' * 55}")
        print(f"CASOS DE TESTE DISPONÍVEIS ({len(TEST_SUITE)} total)")
        print(f"{'─' * 55}")
        for case in TEST_SUITE:
            print(f"  [{case.id}] command={case.command}")
            print(f"    Prompt: \"{case.prompt}\"")
            print(f"    {case.description}")
            print()
        return

    if args.run_suite:
        results = run_suite(args.test_ids, model=args.model)
        if args.output_json and results:
            data = [
                {
                    "id": r.test_id,
                    "passed": r.passed,
                    "score": r.score,
                    "violations": r.violations,
                    "missing": r.missing,
                }
                for r in results
            ]
            with open(args.output_json, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultados salvos em {args.output_json}")
        return

    if args.check_response:
        check_response_file(args.file, args.command)
        return

    parser.print_help()

if __name__ == "__main__":
    main()
