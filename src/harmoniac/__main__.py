"""Ponto de entrada de linha de comando do Harmoniac."""

from harmoniac import __version__


def main() -> None:
    """Imprime a versão atual do Harmoniac."""
    print(f"Harmoniac {__version__}")


if __name__ == "__main__":
    main()
