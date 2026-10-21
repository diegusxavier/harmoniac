"""Reprodução de áudio em tempo real com sounddevice."""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any, Protocol

import sounddevice as sd

from harmoniac.audio.models import AudioData, Samples


class AudioPlaybackError(Exception):
    """Erro ao abrir ou iniciar o dispositivo de áudio."""


class StreamLike(Protocol):
    """Interface mínima de um stream de saída do sounddevice."""

    def start(self) -> None:
        """Inicia o stream."""

    def stop(self) -> None:
        """Para o stream."""

    def close(self) -> None:
        """Libera os recursos do stream."""


StreamFactory = Callable[..., StreamLike]


class BlockReader:
    """Lê blocos de um array de áudio e informa a posição atual.

    O leitor é usado apenas pela thread de áudio. A posição é lida pela
    thread principal; como é um inteiro e só a thread de áudio escreve,
    a leitura é segura sob o GIL.
    """

    def __init__(self, samples: Samples) -> None:
        self._samples = samples
        self._position = 0

    @property
    def position(self) -> int:
        """Quantidade de frames já consumidos."""
        return self._position

    @property
    def finished(self) -> bool:
        """Indica se todas as amostras foram consumidas."""
        return self._position >= int(self._samples.shape[0])

    def fill(self, outdata: Samples) -> None:
        """Preenche outdata com o próximo bloco, completando com zeros.

        Args:
            outdata: Buffer de saída com formato (frames, canais).
        """
        frames = int(outdata.shape[0])
        remaining = int(self._samples.shape[0]) - self._position

        if remaining <= 0:
            outdata.fill(0.0)
            return

        count = min(frames, remaining)
        outdata[:count] = self._samples[self._position : self._position + count]

        if count < frames:
            outdata[count:] = 0.0

        self._position += count


class AudioPlayer:
    """Player baseado em callback do sounddevice.

    O callback roda na thread de áudio do PortAudio. Ele apenas copia
    amostras para o buffer de saída e sinaliza o término; nenhuma
    operação de I/O ou de UI deve ser feita ali.
    """

    def __init__(
        self,
        blocksize: int = 1024,
        stream_factory: StreamFactory | None = None,
    ) -> None:
        if blocksize <= 0:
            raise ValueError("blocksize deve ser positivo")

        self._blocksize = blocksize
        self._stream_factory: StreamFactory = stream_factory or sd.OutputStream
        self._stream: StreamLike | None = None
        self._reader: BlockReader | None = None
        self._samplerate: int | None = None
        self._finished = threading.Event()
        self._finished.set()
        self._had_status = False
        self._lock = threading.Lock()

    def play(self, data: AudioData) -> None:
        """Inicia a reprodução de AudioData em uma thread de áudio.

        Args:
            data: Áudio a ser reproduzido.

        Raises:
            AudioPlaybackError: Se o dispositivo de áudio não puder ser aberto.
        """
        self.stop()
        self._had_status = False

        reader = BlockReader(data.samples)
        finished = threading.Event()

        def callback(
            outdata: Samples,
            _frames: int,
            _time_info: Any,
            status: Any,
        ) -> None:
            if status:
                self._had_status = True

            reader.fill(outdata)
            if reader.finished:
                finished.set()
                raise sd.CallbackStop

        stream: StreamLike | None = None
        try:
            stream = self._stream_factory(
                samplerate=data.samplerate,
                channels=data.channels,
                blocksize=self._blocksize,
                dtype="float32",
                callback=callback,
            )
            stream.start()
        except Exception as exc:
            if stream is not None:
                stream.close()
            raise AudioPlaybackError("Não foi possível iniciar o dispositivo de áudio.") from exc

        with self._lock:
            self._stream = stream
            self._reader = reader
            self._samplerate = data.samplerate
            self._finished = finished

    def wait(self) -> None:
        """Aguarda o término da reprodução atual."""
        self._finished.wait()

    def stop(self) -> None:
        """Para a reprodução atual e libera o stream."""
        with self._lock:
            stream = self._stream
            self._stream = None
            self._reader = None
            self._samplerate = None
            self._finished.set()

        if stream is not None:
            try:
                stream.stop()
            finally:
                stream.close()

    @property
    def is_playing(self) -> bool:
        """Indica se há uma reprodução em andamento."""
        with self._lock:
            return self._stream is not None and not self._finished.is_set()

    @property
    def position_seconds(self) -> float:
        """Posição atual da reprodução em segundos."""
        with self._lock:
            reader = self._reader
            samplerate = self._samplerate

        if reader is None or samplerate is None:
            return 0.0

        return reader.position / samplerate

    @property
    def had_status(self) -> bool:
        """Indica se o callback recebeu algum aviso de underflow/overflow."""
        return self._had_status
