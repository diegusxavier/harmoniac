"""Modelos de dados de áudio do Harmoniac."""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

Samples = npt.NDArray[np.float32]


@dataclass(frozen=True, slots=True)
class AudioData:
    """Áudio digital pronto para reprodução ou processamento.

    Attributes:
        samples: Matriz de formato (frames, canais), com amostras em float32.
        samplerate: Taxa de amostragem em Hz.
    """

    samples: Samples
    samplerate: int

    def __post_init__(self) -> None:
        if self.samples.ndim != 2:
            raise ValueError("samples deve ter formato (frames, canais)")
        if self.samples.dtype != np.float32:
            raise ValueError("samples deve ser float32")
        if self.samplerate <= 0:
            raise ValueError("samplerate deve ser positivo")
        if self.samples.shape[0] == 0:
            raise ValueError("samples não pode estar vazio")
        if self.samples.shape[1] == 0:
            raise ValueError("samples deve ter pelo menos um canal")

    @property
    def frames(self) -> int:
        """Número de amostras por canal."""
        return int(self.samples.shape[0])

    @property
    def channels(self) -> int:
        """Número de canais de áudio."""
        return int(self.samples.shape[1])

    @property
    def duration_seconds(self) -> float:
        """Duração total em segundos."""
        return self.frames / self.samplerate
