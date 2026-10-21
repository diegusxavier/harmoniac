"""Testes do leitor de blocos e do player."""

from typing import Any

import numpy as np
import pytest
import sounddevice as sd

from harmoniac.audio.models import AudioData
from harmoniac.audio.player import AudioPlaybackError, AudioPlayer, BlockReader


class FakeStream:
    """Stream falso para testar o player sem hardware de áudio."""

    def __init__(self, **kwargs: Any) -> None:
        self.callback = kwargs["callback"]
        self.started = False
        self.stopped = False
        self.closed = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def close(self) -> None:
        self.closed = True


def _make_data(frames: int, channels: int = 1) -> AudioData:
    samples = np.arange(frames * channels, dtype=np.float32).reshape(frames, channels)
    return AudioData(samples=samples, samplerate=44100)


def test_block_reader_fills_and_pads() -> None:
    """O leitor deve preencher o bloco e completar com zeros no final."""
    reader = BlockReader(_make_data(5).samples)
    outdata = np.zeros((3, 1), dtype=np.float32)

    reader.fill(outdata)

    assert np.array_equal(outdata[:, 0], np.array([0.0, 1.0, 2.0], dtype=np.float32))
    assert reader.position == 3
    assert not reader.finished

    reader.fill(outdata)

    assert np.array_equal(outdata[:, 0], np.array([3.0, 4.0, 0.0], dtype=np.float32))
    assert reader.position == 5
    assert reader.finished


def test_block_reader_returns_silence_after_end() -> None:
    """Depois do fim, o leitor deve preencher o buffer com silêncio."""
    reader = BlockReader(_make_data(2).samples)
    outdata = np.zeros((2, 1), dtype=np.float32)

    reader.fill(outdata)
    outdata.fill(1.0)
    reader.fill(outdata)

    assert np.array_equal(outdata, np.zeros((2, 1), dtype=np.float32))
    assert reader.position == 2


def test_audio_player_starts_and_stops() -> None:
    """O player deve iniciar e liberar o stream corretamente."""
    streams: list[FakeStream] = []

    def factory(**kwargs: Any) -> FakeStream:
        stream = FakeStream(**kwargs)
        streams.append(stream)
        return stream

    player = AudioPlayer(blocksize=2, stream_factory=factory)
    player.play(_make_data(4))

    assert len(streams) == 1
    assert streams[0].started
    assert player.is_playing

    player.stop()

    assert streams[0].stopped
    assert streams[0].closed
    assert not player.is_playing


def test_audio_player_callback_finishes_and_updates_position() -> None:
    """O callback deve atualizar a posição e sinalizar o término."""
    streams: list[FakeStream] = []

    def factory(**kwargs: Any) -> FakeStream:
        stream = FakeStream(**kwargs)
        streams.append(stream)
        return stream

    player = AudioPlayer(blocksize=2, stream_factory=factory)
    player.play(_make_data(4))
    stream = streams[0]
    outdata = np.zeros((2, 1), dtype=np.float32)

    stream.callback(outdata, 2, None, None)

    assert player.position_seconds == pytest.approx(2 / 44100)
    assert player.is_playing

    with pytest.raises(sd.CallbackStop):
        stream.callback(outdata, 2, None, None)

    assert not player.is_playing
    player.wait()
    player.stop()
    assert stream.stopped
    assert stream.closed


def test_audio_player_wraps_start_error_and_closes_stream() -> None:
    """Falha ao iniciar o stream deve virar AudioPlaybackError e fechar o stream."""

    class FailingStream(FakeStream):
        def start(self) -> None:
            raise RuntimeError("sem dispositivo")

    streams: list[FakeStream] = []

    def factory(**kwargs: Any) -> FakeStream:
        stream = FailingStream(**kwargs)
        streams.append(stream)
        return stream

    player = AudioPlayer(stream_factory=factory)

    with pytest.raises(AudioPlaybackError, match="dispositivo"):
        player.play(_make_data(4))

    assert streams[0].closed
    assert not player.is_playing
