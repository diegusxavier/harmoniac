"""Testes da geração de sinais."""

import numpy as np
import pytest

from harmoniac.audio.signal import generate_sine


def test_generate_sine_shape_and_samplerate() -> None:
    """A senoide deve ter o formato e a taxa de amostragem esperados."""
    data = generate_sine(440.0, 1.0, 44100, channels=2)

    assert data.samplerate == 44100
    assert data.channels == 2
    assert data.frames == 44100
    assert data.samples.dtype == np.float32
    assert data.samples.shape == (44100, 2)


def test_generate_sine_respects_amplitude() -> None:
    """O pico da senoide não deve ultrapassar a amplitude pedida."""
    data = generate_sine(440.0, 0.1, 44100, amplitude=0.5, channels=1)

    assert np.max(np.abs(data.samples)) <= 0.5 + 1e-6


def test_generate_sine_rejects_frequency_above_nyquist() -> None:
    """Frequências acima de Nyquist devem ser rejeitadas."""
    with pytest.raises(ValueError, match="Nyquist"):
        generate_sine(30000.0, 1.0, 44100)


def test_generate_sine_rejects_invalid_duration() -> None:
    """Duração zero ou negativa deve ser rejeitada."""
    with pytest.raises(ValueError, match="duration_seconds"):
        generate_sine(440.0, 0.0, 44100)
