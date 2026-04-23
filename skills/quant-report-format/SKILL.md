# Skill: Análise Quantitativa Formatada (B3 + Cripto)

## Nome
quant-report-format

## Descrição
Template padronizado para análises quantitativas de ações B3, opções B3, criptomoedas e estruturas de derivativos. Garante consistência, rastreabilidade e validação em todos os relatórios do John Galt.

## Quando Usar (Triggers)
Use esta skill **SEMPRE** que John Galt precisar:
- Formatar análise de ações B3 (COGN3, PETR4, VALE3, ITUB4, PCAR3, GMAT3)
- Formatar análise de opções B3 (calls, puts, travas, THL, booster)
- Formatar análise de criptomoedas (BTC, ETH, SOL)
- Enviar relatório quantitativo ao Telegram
- Criar página no Notion com análise
- Validar/corrigir análise prévia
- Gerar relatório semanal/mensal

**Palavras-chave que disparam:**
- "análise quant", "relatório quantitativo"
- "formatar análise", "gerar relatório"
- "validar COGN3", "corrigir análise"
- "enviar ao Telegram", "criar página Notion"
- Qualquer ticker B3 + "análise"
- "Black-Scholes", "Kelly Criterion", "gregas"

## Template Markdown

```markdown
# 📊 ANÁLISE QUANT — {TICKER} — {DD/MM/YYYY}

**Status:** {Em Análise | Validada | Corrigida | Executada}
**Risco/Retorno:** {Conservador | Moderado | Agressivo}
**Recomendação:** {COMPRA | VENDA | HOLD | EVITAR}

---

## 🎯 TESE CENTRAL

{1-2 parágrafos explicando a tese de investimento}

---

## 📈 FUNDAMENTALISTA

| Métrica | Valor | Status |
|---------|-------|--------|
| Preço Atual | R$ X,XX | {Subvalorizado/Justo/Caro} |
| P/L | X,XX | {<15=Atrativo/>20=Caro} |
| P/VP | X,XX | {<1=Barato/>2=Caro} |
| Dividend Yield | X,X% | {>5%=Alto/<2%=Baixo} |
| ROE | X,X% | {>15%=Bom/<10%=Ruim} |
| Upside Graham | XX% | Alvo: R$ X,XX |

---

## 📊 ESTATÍSTICO

| Métrica | Valor | Interpretação |
|---------|-------|---------------|
| Variação 24h | +X,XX% | {Recuperação/Queda} |
| Z-Score | -X,X | {<-1=Deprimido/>+1=Sobrecomprado} |
| HV | XX% | {<20%=Baixa/>40%=Alta} |
| IV | XX% | {Barata/Justa/Cara} |
| IV/HV | X,XX | {<1.0=Barata/>1.2=Cara} |

**Contexto:** {FOMC, COPOM, earnings, etc}

---

## 🎯 ESTRUTURA RECOMENDADA

### {Call ATM / Trava / THL}

**Posição:**
- Ticker: {SERIE}
- Strike: R$ X,XX
- Prêmio: R$ X,XX
- Vencimento: DD/MM/YYYY (XX dias)
- Quantidade: XXX opções

**Financeiro:**
- Break-even: R$ X,XX
- Alvo: R$ X,XX (Ganho: R$ XXX)
- Stop: R$ X,XX (Perda: R$ XXX)

**Gregas:**
- Delta: X,XX (Deep ITM/ATM/OTM)
- Theta: -X,XXX/dia
- P(ITM): XX%

---

## 💰 KELLY CRITERION

- Kelly Full: XX% (R$ X.XXX)
- Kelly 1/4: X% (R$ XXX)
- Quantidade: XXX opções

---

## ⚠️ RISCOS

🔴 **Críticos:** {lista}
🟠 **Altos:** {lista}
🟡 **Médios:** {lista}

📅 **Eventos:**
- DD/MM — FOMC/COPOM/Earnings

---

## 🎯 RECOMENDAÇÃO FINAL

- **Ação:** COMPRA
- **Entrada:** R$ X,XX
- **Stop:** R$ X,XX
- **Alvo:** R$ X,XX
- **Kelly:** X% (R$ XXX)

**P(Sucesso) = XX%**
```

## Regras de Formatação

1. **Precisão numérica:**
   - Preços: 2 casas (R$ 3,27)
   - %: 1 casa (95,5%)
   - Gregas: 2-3 casas (0,95)

2. **Datas:** DD/MM/YYYY

3. **Status:**
   - 🔴 Crítico
   - 🟠 Alto
   - 🟡 Médio
   - 🟢 Baixo
   - ✅ OK
   - ⚠️ Atenção
   - ❌ Erro

4. **Seções obrigatórias:**
   - Tese, Fundamentalista, Estatístico
   - Estrutura, Kelly, Riscos
   - Recomendação Final

## Integração

Após gerar:
1. Criar página Notion: "{TICKER} — Análise — {DD/MM}"
2. Tags: {Ações B3 | Opções | Cripto | THL}
3. Link database "Análises Quantitativas"
4. Enviar ao Telegram se P(Sucesso) > 60%

