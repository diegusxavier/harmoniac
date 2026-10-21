"""Leitura e escrita de arquivos WAV."""

from pathlib import Path

import numpy as np
import soundfile as sf

from harmoniac.audio.models import AudioData


class AudioLoadError(Exception):
    """Erro ao carregar um arquivo de áudio."""


def load_wav(path: Path) -> AudioData:
    """Carrega um arquivo WAV como AudioData float32.

    Args:
        path: Caminho do arquivo WAV.

    Returns:
        AudioData com amostras no formato (frames, canais).

    Raises:
        AudioLoadError: Se o arquivo não existir ou não puder ser lido.
    """
    try:
        samples, samplerate = sf.read(path, dtype="float32", always_2d=True)
    except (OSError, RuntimeError) as exc:
        raise AudioLoadError(f"Falha ao carregar o arquivo WAV: {path}") from exc

    samples_array = np.asarray(samples, dtype=np.float32)
    return AudioData(samples=samples_array, samplerate=int(samplerate))


def save_wav(path: Path, data: AudioData, *, subtype: str = "FLOAT") -> None:
    """Salva AudioData em um arquivo WAV.

    Args:
        path: Caminho de destino.
        data: Áudio a ser salvo.
        subtype: Subtipo do WAV (por exemplo, "FLOAT" ou "PCM_16").
    """
    sf.write(path, data.samples, data.samplerate, subtype=subtype)
