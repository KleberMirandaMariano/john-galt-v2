"""Testes para read_cache.py"""
import json
import sys
import os
import time
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestCacheReader:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        with patch.dict(os.environ, {'ZEROCLAW_WORKSPACE': self.tmpdir}):
            # Reimport para pegar o env atualizado
            if 'read_cache' in sys.modules:
                del sys.modules['read_cache']
            from read_cache import CacheReader
            self.CacheReader = CacheReader

    def _make_reader(self, max_age_minutes=60):
        reader = self.CacheReader(max_age_minutes=max_age_minutes)
        reader.workspace = Path(self.tmpdir)
        return reader

    def test_no_cripto_cache_returns_no_cache_status(self):
        reader = self._make_reader()
        result = reader.load_cripto_cache()
        assert result['status'] == 'No cache'

    def test_valid_cripto_cache_returns_ok(self):
        data = {
            "bitcoin": {"usd": 95000, "usd_24h_change": 1.5},
            "ethereum": {"usd": 3200, "usd_24h_change": -0.8},
            "solana": {"usd": 150, "usd_24h_change": 2.1}
        }
        cache_file = Path(self.tmpdir) / ".cripto_cache.json"
        cache_file.write_text(json.dumps(data))

        reader = self._make_reader()
        result = reader.load_cripto_cache()
        assert result['status'] == 'OK'
        assert result['btc_price'] == 95000
        assert result['eth_price'] == 3200
        assert result['sol_price'] == 150

    def test_stale_cache_returns_stale_status(self):
        cache_file = Path(self.tmpdir) / ".cripto_cache.json"
        cache_file.write_text(json.dumps({"bitcoin": {"usd": 90000}}))

        # Modificar mtime para simular cache antigo (2 horas atrás)
        old_time = time.time() - 7200
        os.utime(cache_file, (old_time, old_time))

        reader = self._make_reader(max_age_minutes=60)
        result = reader.load_cripto_cache()
        assert result['status'] == 'Stale'

    def test_fresh_cache_not_stale(self):
        data = {"bitcoin": {"usd": 95000, "usd_24h_change": 0.5},
                "ethereum": {"usd": 3200, "usd_24h_change": 0.1},
                "solana": {"usd": 150, "usd_24h_change": 0.2}}
        cache_file = Path(self.tmpdir) / ".cripto_cache.json"
        cache_file.write_text(json.dumps(data))

        reader = self._make_reader(max_age_minutes=60)
        result = reader.load_cripto_cache()
        assert result['status'] == 'OK'

    def test_invalid_json_returns_error(self):
        cache_file = Path(self.tmpdir) / ".cripto_cache.json"
        cache_file.write_text("isso nao eh json valido {{{{")

        reader = self._make_reader()
        result = reader.load_cripto_cache()
        assert result['status'] == 'Error'

    def test_no_fng_cache(self):
        reader = self._make_reader()
        result = reader.load_fng_cache()
        assert result['status'] == 'No cache'

    def test_valid_fng_cache(self):
        data = {"value": "42", "value_classification": "Fear", "timestamp": "1234567890"}
        cache_file = Path(self.tmpdir) / ".fng_cache.json"
        cache_file.write_text(json.dumps(data))

        reader = self._make_reader()
        result = reader.load_fng_cache()
        assert result['status'] == 'OK'
        assert result['fng_value'] == "42"
        assert result['fng_label'] == "Fear"

    def test_get_all_cache_returns_four_keys(self):
        reader = self._make_reader()
        result = reader.get_all_cache()
        assert 'cripto' in result
        assert 'fng' in result
        assert 'b3' in result
        assert 'news' in result
        assert 'timestamp' in result

    def test_no_b3_cache(self):
        reader = self._make_reader()
        result = reader.load_b3_cache()
        assert result['status'] == 'No cache'

    def test_valid_b3_cache(self):
        content = "# header\nCOGN3|3.27|+0.92%\nPETR4|38.50|-0.5%\n"
        cache_file = Path(self.tmpdir) / "b3_cotacoes.txt"
        cache_file.write_text(content)

        reader = self._make_reader()
        result = reader.load_b3_cache()
        assert result['status'] == 'OK'
        assert result['count'] == 2
        assert 'COGN3' in result['tickers']
