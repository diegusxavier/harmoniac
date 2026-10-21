"""Testes de fumaça da fundação do pacote Harmoniac."""

import pytest

from harmoniac import __version__
from harmoniac.__main__ import main


def test_version() -> None:
    """A versão do pacote deve corresponder à versão declarada no pyproject."""
    assert __version__ == "0.1.0"


def test_main_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    """O CLI deve imprimir a versão com --version."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_main_without_command_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Sem subcomando, o CLI deve exibir a ajuda."""
    main([])

    captured = capsys.readouterr()
    assert "usage:" in captured.out
