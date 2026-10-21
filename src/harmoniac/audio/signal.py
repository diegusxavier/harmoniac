"""Geração de sinais de teste."""

import numpy as np

from harmoniac.audio.models import AudioData


def generate_sine(
    frequency_hz: float,
    duration_seconds: float,
    samplerate: int,
    amplitude: float = 0.2,
    channels: int = 2,
) -> AudioData:
    """Gera uma senoide com duração e taxa de amostragem definidas.

    A frequência precisa estar abaixo da frequência de Nyquist
    (samplerate / 2) para evitar aliasing.

    Args:
        frequency_hz: Frequência da senoide em Hz.
        duration_seconds: Duração em segundos.
        samplerate: Taxa de amostragem em Hz.
        amplitude: Amplitude linear entre 0 e 1.
        channels: Número de canais (1 = mono, 2 = estéreo).

    Returns:
        AudioData com amostras float32 no formato (frames, canais).

    Raises:
        ValueError: Se algum parâmetro estiver fora da faixa válida.
    """
    if samplerate <= 0:
        raise ValueError("samplerate deve ser positivo")
    if not 0 < frequency_hz < samplerate / 2:
        raise ValueError("frequency_hz deve ficar entre 0 e a frequência de Nyquist")
    if duration_seconds <= 0:
        raise ValueError("duration_seconds deve ser positivo")
    if not 0 < amplitude <= 1:
        raise ValueError("amplitude deve ficar entre 0 e 1")
    if channels <= 0:
        raise ValueError("channels deve ser positivo")

    frames = round(duration_seconds * samplerate)
    if frames <= 0:
        raise ValueError("duration_seconds gera menos de uma amostra")

    time = np.arange(frames, dtype=np.float64) / samplerate
    wave = amplitude * np.sin(2 * np.pi * frequency_hz * time)
    samples = np.repeat(wave[:, np.newaxis], channels, axis=1).astype(np.float32)
    return AudioData(samples=samples, samplerate=samplerate)
