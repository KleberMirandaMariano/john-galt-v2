# Fear & Greed Index — Live

## Quando usar
Sempre que o usuário perguntar sobre sentimento do mercado cripto, Fear & Greed, ou quando for incluir esse dado em qualquer análise ou relatório.

## Como buscar o dado real

Execute SEMPRE antes de mencionar o Fear & Greed:

```
web_fetch("https://api.alternative.me/fng/?limit=1")
→ data[0]['value']                  # número 0-100
→ data[0]['value_classification']   # texto: "Fear", "Greed", etc.
```

Extraia e formate inline:
```
fng_value = data[0]['value']
fng_label = data[0]['value_classification']
→ "Fear & Greed: {fng_value} ({fng_label})"
```

## Interpretação
- 0-24: Medo Extremo (oportunidade de compra)
- 25-44: Medo
- 45-55: Neutro
- 56-74: Ganância
- 75-100: Ganância Extrema (sinal de topo)

## REGRA CRÍTICA
NUNCA mencione o Fear & Greed Index sem executar o web_fetch acima.
Se a API falhar, diga: "Fear & Greed indisponível no momento."
JAMAIS invente ou estime esse valor.
