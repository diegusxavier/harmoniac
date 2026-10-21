"""Ponto de entrada de linha de comando do Harmoniac."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from harmoniac import __version__
from harmoniac.audio.models import AudioData
from harmoniac.audio.player import AudioPlaybackError, AudioPlayer
from harmoniac.audio.signal import generate_sine
from harmoniac.audio.wav import AudioLoadError, load_wav


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser de argumentos do CLI."""
    parser = argparse.ArgumentParser(
        prog="harmoniac",
        description="Treinador musical de precisão com sincronização orientada a eventos.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    demo = subparsers.add_parser("demo", help="Toca uma senoide de teste.")
    demo.add_argument("--frequency", type=float, default=440.0, help="Frequência em Hz.")
    demo.add_argument("--duration", type=float, default=3.0, help="Duração em segundos.")
    demo.add_argument("--samplerate", type=int, default=44100, help="Taxa de amostragem.")
    demo.add_argument("--amplitude", type=float, default=0.2, help="Amplitude entre 0 e 1.")
    demo.add_argument("--channels", type=int, default=2, help="Número de canais.")

    play = subparsers.add_parser("play", help="Toca um arquivo WAV.")
    play.add_argument("path", type=Path, help="Caminho do arquivo WAV.")

    return parser


def _play(data: AudioData) -> None:
    """Reproduz AudioData e aguarda o término."""
    player = AudioPlayer()
    try:
        player.play(data)
        player.wait()
    except AudioPlaybackError as exc:
        print(f"Erro de áudio: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    finally:
        player.stop()


def main(argv: Sequence[str] | None = None) -> None:
    """Executa o CLI do Harmoniac."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "demo":
        try:
            data = generate_sine(
                frequency_hz=args.frequency,
                duration_seconds=args.duration,
                samplerate=args.samplerate,
                amplitude=args.amplitude,
                channels=args.channels,
            )
        except ValueError as exc:
            parser.error(str(exc))
        _play(data)
        return

    if args.command == "play":
        try:
            data = load_wav(args.path)
        except AudioLoadError as exc:
            print(f"Erro: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        _play(data)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
