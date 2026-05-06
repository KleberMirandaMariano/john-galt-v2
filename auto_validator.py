#!/usr/bin/env python3
"""
Auto Validator for John Galt
Validates analysis before sending to user
Checks: data freshness, required metrics, calculations
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class AutoValidator:
    """
    Sistema de validação automática de análises
    
    Valida:
    - Freshness de dados (< 24h)
    - Métricas obrigatórias presentes
    - Cálculos matemáticos corretos
    - Greeks dentro de ranges válidos
    """
    
    def __init__(self):
        self.rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict:
        """
        Carrega regras de validação baseadas em erros históricos
        
        Returns:
            Dict com regras de validação
        """
        return {
            "data_freshness": {
                "max_age_hours": 24,
                "critical": True
            },
            "required_metrics": {
                "cripto": [
                    "spot_price",
                    "iv_atm",
                    "historical_vol",
                    "correlation_btc",
                    "fear_greed_index"
                ],
                "b3": [
                    "spot_price",
                    "iv_atm",
                    "historical_vol"
                ]
            },
            "greeks_ranges": {
                "delta": {"min": -1.0, "max": 1.0},
                "theta": {"max": 0.0},  # Theta deve ser <= 0 para compras
                "vega": {"min": 0.0},
                "gamma": {"min": 0.0}
            },
            "required_calculations": {
                "black_scholes": True,
                "greeks": ["delta", "theta", "vega", "gamma"],
                "scenarios": True,
                "risk_reward": True
            }
        }
    
    def validate(self, analysis: Dict, market: str = "cripto") -> Dict:
        """
        Valida análise completa
        
        Args:
            analysis: Dict com análise gerada
            market: "cripto" ou "b3"
        
        Returns:
            Dict com:
            - valid: bool
            - errors: List[str] (críticos)
            - warnings: List[str] (não-críticos)
            - score: float (0.0-1.0)
        """
        
        errors = []
        warnings = []
        
        # Validar freshness de dados
        freshness_ok, freshness_msg = self._check_data_freshness(analysis)
        if not freshness_ok:
            errors.append(freshness_msg)
        
        # Validar métricas obrigatórias
        missing = self._check_required_metrics(analysis, market)
        if missing:
            errors.append(f"Métricas faltando: {', '.join(missing)}")
        
        # Validar cálculos Black-Scholes
        bs_issues = self._validate_black_scholes(analysis)
        if bs_issues:
            warnings.extend(bs_issues)
        
        # Validar Greeks
        greeks_issues = self._validate_greeks(analysis)
        if greeks_issues:
            errors.extend(greeks_issues)
        
        # Validar estruturas de opções
        structure_issues = self._validate_structures(analysis)
        if structure_issues:
            warnings.extend(structure_issues)
        
        # Calcular score de qualidade
        total_checks = 5
        passed_checks = (
            (1 if freshness_ok else 0) +
            (1 if not missing else 0) +
            (1 if not bs_issues else 0.5) +
            (1 if not greeks_issues else 0) +
            (1 if not structure_issues else 0.5)
        )
        
        score = passed_checks / total_checks
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "score": round(score, 2),
            "checks_passed": int(passed_checks),
            "total_checks": total_checks
        }
    
    def _check_data_freshness(self, analysis: Dict) -> Tuple[bool, str]:
        """
        Verifica se dados não estão velhos demais
        
        Args:
            analysis: Dict com análise
        
        Returns:
            Tuple (is_fresh: bool, message: str)
        """
        
        timestamp = analysis.get("timestamp")
        if not timestamp:
            return False, "Timestamp ausente - não é possível validar freshness"
        
        try:
            data_time = datetime.fromisoformat(timestamp)
        except ValueError:
            return False, f"Timestamp inválido: {timestamp}"
        
        now = datetime.now()
        age_hours = (now - data_time).total_seconds() / 3600
        
        max_age = self.rules["data_freshness"]["max_age_hours"]
        
        if age_hours > max_age:
            return False, f"Dados com {age_hours:.1f}h (máx: {max_age}h)"
        
        return True, ""
    
    def _check_required_metrics(
        self, 
        analysis: Dict, 
        market: str
    ) -> List[str]:
        """
        Verifica métricas obrigatórias
        
        Args:
            analysis: Dict com análise
            market: "cripto" ou "b3"
        
        Returns:
            Lista de métricas faltando
        """
        
        required = self.rules["required_metrics"].get(market, [])
        missing = []
        
        for metric in required:
            if metric not in analysis or analysis[metric] is None:
                missing.append(metric)
        
        return missing
    
    def _validate_black_scholes(self, analysis: Dict) -> List[str]:
        """
        Valida cálculos Black-Scholes
        
        Args:
            analysis: Dict com análise
        
        Returns:
            Lista de issues encontrados
        """
        
        issues = []
        
        if "black_scholes" not in analysis:
            issues.append("Black-Scholes não calculado")
            return issues
        
        bs = analysis["black_scholes"]
        
        # Call price não pode ser negativo
        if bs.get("call_price", 0) < 0:
            issues.append("BS: Call price negativo")
        
        # Put price não pode ser negativo
        if bs.get("put_price", 0) < 0:
            issues.append("BS: Put price negativo")
        
        # IV deve ser > 0
        if bs.get("iv", 0) <= 0:
            issues.append("BS: IV inválido (<= 0)")
        
        return issues
    
    def _validate_greeks(self, analysis: Dict) -> List[str]:
        """
        Valida Greeks dentro de ranges válidos
        
        Args:
            analysis: Dict com análise
        
        Returns:
            Lista de erros encontrados
        """
        
        errors = []
        
        if "greeks" not in analysis:
            errors.append("Greeks não calculados")
            return errors
        
        greeks = analysis["greeks"]
        ranges = self.rules["greeks_ranges"]
        
        # Validar Delta (-1 a +1)
        delta = greeks.get("delta")
        if delta is not None:
            if delta < ranges["delta"]["min"] or delta > ranges["delta"]["max"]:
                errors.append(
                    f"Delta fora do range: {delta} "
                    f"(válido: {ranges['delta']['min']} a {ranges['delta']['max']})"
                )
        
        # Validar Theta (deve ser <= 0 para compras)
        theta = greeks.get("theta")
        if theta is not None:
            if theta > ranges["theta"]["max"]:
                errors.append(
                    f"Theta positivo para compra: {theta} "
                    f"(deve ser <= {ranges['theta']['max']})"
                )
        
        # Validar Vega (deve ser >= 0)
        vega = greeks.get("vega")
        if vega is not None:
            if vega < ranges["vega"]["min"]:
                errors.append(
                    f"Vega negativo: {vega} "
                    f"(deve ser >= {ranges['vega']['min']})"
                )
        
        # Validar Gamma (deve ser >= 0)
        gamma = greeks.get("gamma")
        if gamma is not None:
            if gamma < ranges["gamma"]["min"]:
                errors.append(
                    f"Gamma negativo: {gamma} "
                    f"(deve ser >= {ranges['gamma']['min']})"
                )
        
        return errors
    
    def _validate_structures(self, analysis: Dict) -> List[str]:
        """
        Valida estruturas de opções recomendadas
        
        Args:
            analysis: Dict com análise
        
        Returns:
            Lista de warnings
        """
        
        warnings = []
        
        if "recommended_structures" not in analysis:
            warnings.append("Nenhuma estrutura recomendada")
            return warnings
        
        structures = analysis["recommended_structures"]
        
        for structure in structures:
            # Validar que estrutura tem risk/reward
            if "risk_reward" not in structure:
                warnings.append(
                    f"Estrutura '{structure.get('name')}' sem risk/reward"
                )
            
            # Validar que estrutura tem break-even
            if "break_even" not in structure:
                warnings.append(
                    f"Estrutura '{structure.get('name')}' sem break-even"
                )
            
            # Validar que estrutura tem cenários
            if "scenarios" not in structure:
                warnings.append(
                    f"Estrutura '{structure.get('name')}' sem cenários"
                )
        
        return warnings
    
    def generate_validation_report(self, validation: Dict) -> str:
        """
        Gera relatório de validação formatado
        
        Args:
            validation: Resultado de validate()
        
        Returns:
            String com relatório formatado
        """
        
        report = []
        
        report.append("=" * 60)
        report.append("VALIDATION REPORT")
        report.append("=" * 60)
        
        # Status
        status = "✅ PASSED" if validation["valid"] else "❌ FAILED"
        report.append(f"Status: {status}")
        report.append(f"Score: {validation['score']:.2f}")
        report.append(
            f"Checks: {validation['checks_passed']}/{validation['total_checks']}"
        )
        
        # Errors
        if validation["errors"]:
            report.append("\n🚨 ERRORS (CRITICAL):")
            for error in validation["errors"]:
                report.append(f"  - {error}")
        
        # Warnings
        if validation["warnings"]:
            report.append("\n⚠️  WARNINGS:")
            for warning in validation["warnings"]:
                report.append(f"  - {warning}")
        
        if validation["valid"]:
            report.append("\n✅ Analysis ready to send!")
        else:
            report.append("\n❌ Fix errors before sending!")
        
        report.append("=" * 60)
        
        return "\n".join(report)


# Exemplo de uso
if __name__ == "__main__":
    validator = AutoValidator()
    
    # Análise de exemplo
    sample_analysis = {
        "timestamp": datetime.now().isoformat(),
        "spot_price": 88.88,
        "iv_atm": 85.0,
        "historical_vol": 92.5,
        "correlation_btc": 0.78,
        "fear_greed_index": 65,
        "black_scholes": {
            "call_price": 3.45,
            "put_price": 2.89,
            "iv": 85.0
        },
        "greeks": {
            "delta": 0.55,
            "theta": -0.12,
            "vega": 0.18,
            "gamma": 0.025
        },
        "recommended_structures": [
            {
                "name": "Bull Call Spread",
                "risk_reward": 2.5,
                "break_even": 90.50,
                "scenarios": {
                    "alta": "+250%",
                    "baixa": "-100%",
                    "lateral": "-30%"
                }
            }
        ]
    }
    
    # Validar
    validation = validator.validate(sample_analysis, market="cripto")
    
    # Gerar relatório
    report = validator.generate_validation_report(validation)
    print(report)
    
    # JSON output
    print("\nJSON Output:")
    print(json.dumps(validation, indent=2))
