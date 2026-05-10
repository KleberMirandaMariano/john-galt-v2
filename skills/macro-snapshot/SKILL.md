# Macro Snapshot — Brasil e Global

## Quando usar
Quando o usuário pedir macro, panorama econômico, Selic, câmbio, ou quando for incluir dados macro em análises.

## Dados disponíveis via web_fetch (sem autenticação)

### USD/BRL e Ibovespa via BRAPI
```
web_fetch("https://brapi.dev/api/quote/USDBRL,^BVSP?token=tP2QrzuthuXx4JjrnBqnkd")
→ results[0].regularMarketPrice        # preço atual
→ results[0].regularMarketChangePercent # variação %
```

### Selic via API BCB
```
web_fetch("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json")
→ [0]['valor']  # taxa Selic em % a.a.
→ [0]['data']   # data de referência
```

### Câmbio BRL/USD
```
web_fetch("https://economia.awesomeapi.com.br/json/last/USD-BRL")
→ USDBRL.bid    # cotação de compra
→ USDBRL.pctChange # variação %
```

## Formato de resposta esperado
```
🇧🇷 MACRO BRASIL — [DATA]

💰 USD/BRL: R$ X.XX (+X.XX%)
📈 Ibovespa: XXX.XXX pts (+X.XX%)
🏦 Selic: XX.XX% a.a. (ref: DD/MM/AAAA)
```

## REGRA CRÍTICA
Execute os web_fetch acima antes de mencionar qualquer dado macro.
Se uma API falhar, indique: "Dado indisponível — consulte [fonte]."
NUNCA estime Selic, câmbio ou CDS sem fonte verificável.
