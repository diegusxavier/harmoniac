"""Testes de leitura e escrita de WAV."""

from pathlib import Path

import numpy as np
import pytest

from harmoniac.audio.models import AudioData
from harmoniac.audio.signal import generate_sine
from harmoniac.audio.wav import AudioLoadError, load_wav, save_wav


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    """Salvar e carregar deve preservar taxa, canais e amostras."""
    data = generate_sine(440.0, 0.05, 44100, amplitude=0.3, channels=2)
    path = tmp_path / "teste.wav"

    save_wav(path, data)
    loaded = load_wav(path)

    assert loaded.samplerate == data.samplerate
    assert loaded.channels == data.channels
    assert loaded.frames == data.frames
    assert np.allclose(loaded.samples, data.samples, atol=1e-6)


def test_load_wav_missing_file(tmp_path: Path) -> None:
    """Arquivo inexistente deve gerar AudioLoadError."""
    with pytest.raises(AudioLoadError):
        load_wav(tmp_path / "nao-existe.wav")


def test_load_wav_mono(tmp_path: Path) -> None:
    """WAV mono deve continuar com um canal após o carregamento."""
    data = generate_sine(220.0, 0.02, 22050, channels=1)
    path = tmp_path / "mono.wav"
    save_wav(path, data)

    loaded = load_wav(path)

    assert loaded.channels == 1
    assert loaded.samples.shape == (data.frames, 1)


def test_audio_data_rejects_invalid_dtype() -> None:
    """AudioData deve exigir amostras em float32."""
    with pytest.raises(ValueError):
        AudioData(samples=np.zeros((10, 2), dtype=np.float64), samplerate=44100)


def test_audio_data_rejects_1d_samples() -> None:
    """AudioData deve exigir uma matriz (frames, canais)."""
    with pytest.raises(ValueError):
        AudioData(samples=np.zeros(10, dtype=np.float32), samplerate=44100)
