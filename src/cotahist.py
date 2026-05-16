#!/usr/bin/env python3
"""
cotahist.py - Cliente COTAHIST para spot price e cadeia de opções B3.

Baixa e parseia o arquivo histórico diário da B3 (formato fixo, Latin-1).
Provê preço real e chain completa de PUT/CALL — substitui a estimativa
Black-Scholes com IV hardcoded de analyze_ticker.py.

Fonte: https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_D{DDMMYYYY}.ZIP
Formato: linhas de 246 chars, sem separadores, encoding Latin-1

Campo          Posição    Descrição
tipreg         0:2        Tipo do registro ("01" = dado de negócio)
codneg         12:24      Código de negociação (ticker)
tpmerc         24:27      Tipo de mercado (010=vista, 070=CALL, 080=PUT)
preult         108:121    Preço do último negócio (centavos)
voltot         170:188    Volume total negociado (centavos)
preexe         188:201    Preço de exercício — opções (centavos)
datven         202:210    Data de vencimento — opções (YYYYMMDD)
"""

import io
import json
import os
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

COTAHIST_URL = (
    "https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_D{date}.ZIP"
)
DEFAULT_CACHE = "/root/.zeroclaw/workspace/cotahist_cache.json"

_VISTA = "010"
_CALL  = "070"
_PUT   = "080"

# slices para o formato fixo
_S_TIPREG = slice(0, 2)
_S_CODNEG = slice(12, 24)
_S_TPMERC = slice(24, 27)
_S_PREULT = slice(108, 121)
_S_VOLTOT = slice(170, 188)
_S_PREEXE = slice(188, 201)
_S_DATVEN = slice(202, 210)


class CotahistClient:
    """
    Cliente para o arquivo COTAHIST diário da B3.

    Uso típico:
        client = CotahistClient()
        quote  = client.get_quote("COGN3")    # {"preco", "volume", "data_ref"}
        chain  = client.get_options("COGN3")  # list de {"ticker","tipo","strike","preco",...}
    """

    def __init__(self, cache_file: str = DEFAULT_CACHE):
        self.cache_file = cache_file
        self._stocks: Dict[str, Dict] = {}
        self._options: Dict[str, List] = {}
        self._date_ref: Optional[str] = None
        self._loaded = False

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def load(self) -> bool:
        """Garante que os dados estão disponíveis (cache ou download)."""
        if self._loaded:
            return True
        if self._load_cache():
            self._loaded = True
            return True
        content = self._download()
        if content is None:
            return False
        self._parse(content)
        self._save_cache()
        self._loaded = True
        return True

    def get_quote(self, ticker: str) -> Optional[Dict]:
        """
        Retorna cotação spot do ticker.

        Returns:
            {"preco": float, "volume": float, "data_ref": str, "fonte": "cotahist"}
            ou None se não encontrado.
        """
        if not self.load():
            return None
        data = self._stocks.get(ticker.upper())
        if data:
            return {**data, "data_ref": self._date_ref, "fonte": "cotahist"}
        return None

    def get_options(self, ticker: str, max_vencimentos: int = 3) -> List[Dict]:
        """
        Retorna chain de opções do ticker (PUT + CALL).

        Retorna os próximos `max_vencimentos` vencimentos por tipo,
        ordenados por (tipo, vencimento, strike).

        Returns:
            [{"ticker", "tipo", "strike", "preco", "vencimento", "volume"}]
        """
        if not self.load():
            return []

        ticker = ticker.upper()
        # COTAHIST indexa pelo prefixo de 4 chars do código do objeto
        all_opts = self._options.get(ticker[:4], [])
        if not all_opts:
            return []

        today = datetime.now().strftime("%Y-%m-%d")
        future = [o for o in all_opts if o["vencimento"] >= today and o["preco"] > 0]

        selected: List[Dict] = []
        for tipo in ("CALL", "PUT"):
            tipo_opts = [o for o in future if o["tipo"] == tipo]
            vencimentos = sorted(set(o["vencimento"] for o in tipo_opts))
            for venc in vencimentos[:max_vencimentos]:
                selected.extend(o for o in tipo_opts if o["vencimento"] == venc)

        return sorted(selected, key=lambda x: (x["tipo"], x["vencimento"], x["strike"]))

    def stats(self) -> Dict:
        """Sumário: quantas ações e opções indexadas."""
        total_opts = sum(len(v) for v in self._options.values())
        return {
            "data_ref": self._date_ref,
            "acoes": len(self._stocks),
            "tickers_com_opcoes": len(self._options),
            "total_opcoes": total_opts,
        }

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    def _download(self) -> Optional[str]:
        today = datetime.now()
        for delta in range(7):
            d = today - timedelta(days=delta)
            if d.weekday() >= 5:
                continue
            date_str = d.strftime("%d%m%Y")
            url = COTAHIST_URL.format(date=date_str)
            try:
                resp = requests.get(url, timeout=45)
                if resp.status_code == 200:
                    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                        content = zf.read(zf.namelist()[0]).decode("latin-1")
                    self._date_ref = d.strftime("%Y-%m-%d")
                    kb = len(resp.content) // 1024
                    print(f"  [cotahist] baixado {date_str} ({kb} KB)")
                    return content
            except Exception as e:
                print(f"  [cotahist] {date_str}: {e}")
        print("  [cotahist] ❌ não foi possível baixar")
        return None

    # ------------------------------------------------------------------
    # Parse (formato fixo 246 chars)
    # ------------------------------------------------------------------

    def _parse(self, content: str):
        stocks: Dict[str, Dict] = {}
        options: Dict[str, List] = {}

        for line in content.splitlines():
            if len(line) < 245:
                continue
            if line[_S_TIPREG] != "01":
                continue

            tpmerc = line[_S_TPMERC]
            if tpmerc not in (_VISTA, _CALL, _PUT):
                continue

            try:
                codneg = line[_S_CODNEG].strip()
                preult = int(line[_S_PREULT]) / 100.0
                voltot = int(line[_S_VOLTOT]) / 100.0
            except (ValueError, IndexError):
                continue

            if tpmerc == _VISTA:
                stocks[codneg] = {"preco": preult, "volume": voltot}

            else:
                try:
                    preexe = int(line[_S_PREEXE]) / 100.0
                    datven = datetime.strptime(
                        line[_S_DATVEN].strip(), "%Y%m%d"
                    ).strftime("%Y-%m-%d")
                except (ValueError, IndexError):
                    continue

                tipo = "CALL" if tpmerc == _CALL else "PUT"
                ticker_obj = codneg[:4]

                options.setdefault(ticker_obj, []).append({
                    "ticker": codneg,
                    "tipo": tipo,
                    "strike": preexe,
                    "preco": preult,
                    "vencimento": datven,
                    "volume": voltot,
                })

        self._stocks = stocks
        self._options = options
        print(
            f"  [cotahist] parseado: {len(stocks)} ações, "
            f"{sum(len(v) for v in options.values())} opções"
        )

    # ------------------------------------------------------------------
    # Cache JSON (válido pelo mesmo dia de pregão)
    # ------------------------------------------------------------------

    def _load_cache(self) -> bool:
        if not os.path.exists(self.cache_file):
            return False
        try:
            with open(self.cache_file) as f:
                cache = json.load(f)
            if cache.get("data_ref") != datetime.now().strftime("%Y-%m-%d"):
                return False
            self._stocks = cache["stocks"]
            self._options = cache["options"]
            self._date_ref = cache["data_ref"]
            total = sum(len(v) for v in self._options.values())
            print(
                f"  [cotahist] cache {self._date_ref}: "
                f"{len(self._stocks)} ações, {total} opções"
            )
            return True
        except Exception:
            return False

    def _save_cache(self):
        os.makedirs(os.path.dirname(self.cache_file) or ".", exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(
                {
                    "data_ref": self._date_ref,
                    "gerado_em": datetime.now().isoformat(),
                    "stocks": self._stocks,
                    "options": self._options,
                },
                f,
            )
