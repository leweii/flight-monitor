# tests/test_fetchers_base.py
import pytest
from datetime import date
from src.fetchers.base import BaseFetcher

def test_base_fetcher_is_abstract():
    with pytest.raises(TypeError):
        BaseFetcher()

def test_base_fetcher_subclass():
    class MockFetcher(BaseFetcher):
        @property
        def source_name(self) -> str:
            return "mock"

        async def fetch(self, origin, destination, date_start, date_end):
            return []

        def is_available(self) -> bool:
            return True

    fetcher = MockFetcher()
    assert fetcher.source_name == "mock"
    assert fetcher.is_available() is True
