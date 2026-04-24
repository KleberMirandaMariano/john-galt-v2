# Fear & Greed Index — Live

## Quando usar
Sempre que o usuário perguntar sobre sentimento do mercado cripto, Fear & Greed, ou quando for incluir esse dado em qualquer análise ou relatório.

## Como buscar o dado real

Execute SEMPRE antes de mencionar o Fear & Greed:

shell: curl -s "https://api.alternative.me/fng/?limit=1" | python3 -c "
import json,sys
d=json.load(sys.stdin)['data'][0]
print(f\"Fear & Greed: {d['value']} ({d['value_classification']})\")
"

## Interpretação
- 0-24: Medo Extremo (oportunidade de compra)
- 25-44: Medo
- 45-55: Neutro
- 56-74: Ganância
- 75-100: Ganância Extrema (sinal de topo)

## REGRA CRÍTICA
NUNCA mencione o Fear & Greed Index sem executar o curl acima.
Se o curl falhar, diga: "Fear & Greed indisponível no momento."
JAMAIS invente ou estime esse valor.
