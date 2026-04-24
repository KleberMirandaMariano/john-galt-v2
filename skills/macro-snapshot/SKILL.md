# Macro Snapshot — Brasil e Global

## Quando usar
Quando o usuário pedir macro, panorama econômico, Selic, câmbio, ou quando for incluir dados macro em análises.

## Dados disponíveis via API (sem autenticação)

### USD/BRL e Ibovespa via BRAPI
shell: curl -s "https://brapi.dev/api/quote/USDBRL,^BVSP?token=tP2QrzuthuXx4JjrnBqnkd" | python3 -c "
import json,sys
d=json.load(sys.stdin)['results']
for item in d:
    print(f\"{item['symbol']}: {item.get('regularMarketPrice','N/A')} ({item.get('regularMarketChangePercent',0):.2f}%)\")
"

### Selic via API BCB
shell: curl -s "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json" | python3 -c "
import json,sys
d=json.load(sys.stdin)[0]
print(f\"Selic: {d['valor']}% a.a. (ref: {d['data']})\")
"

### CDS Brasil 5Y (via Yahoo Finance proxy)
shell: curl -s "https://brapi.dev/api/quote/BRLUSD=X?token=tP2QrzuthuXx4JjrnBqnkd" | python3 -c "
import json,sys
d=json.load(sys.stdin)['results'][0]
print(f\"BRL/USD: {d.get('regularMarketPrice','N/A')}\")
"

## REGRA CRÍTICA
Execute os curls acima antes de mencionar qualquer dado macro.
Se uma API falhar, indique: "Dado indisponível — consulte [fonte]."
NUNCA estime Selic, câmbio ou CDS sem fonte verificável.
