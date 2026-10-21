"""Testes de fumaça da fundação do pacote Harmoniac."""

import pytest

from harmoniac import __version__
from harmoniac.__main__ import main


def test_version() -> None:
    """A versão do pacote deve corresponder à versão declarada no pyproject."""
    assert __version__ == "0.1.0"


def test_main_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    """O CLI mínimo deve imprimir a versão do Harmoniac."""
    main()
    captured = capsys.readouterr()
    assert captured.out.strip() == f"Harmoniac {__version__}"
