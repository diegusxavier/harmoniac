# Fase 1 — Engine de Áudio

## 1. Objetivo

A Fase 1 implementa a primeira camada de áudio do Harmoniac: representar,
gerar, carregar, salvar e reproduzir áudio digital. Ela ainda não tem interface
gráfica, mixer, metrônomo ou análise musical.

Ao final desta fase, o projeto deve ser capaz de:

- representar áudio como uma matriz `(frames, canais)` em `float32`;
- gerar uma senoide de teste;
- carregar e salvar arquivos WAV;
- reproduzir áudio com `sounddevice` usando callback;
- informar posição, término e ocorrência de underrun/overrun;
- expor tudo isso em um CLI simples.

## 2. Escopo

### Dentro do escopo

- Modelo `AudioData` com validações.
- Geração de senoide.
- Leitura e escrita de WAV com `soundfile`.
- `BlockReader` para leitura em blocos.
- `AudioPlayer` baseado em callback do `sounddevice`.
- Injeção de stream para testes sem hardware.
- CLI `harmoniac demo` e `harmoniac play`.
- Testes unitários, lint, formatação e tipagem.

### Fora do escopo

- Mixer, ganhos, pan e Clear Tracks.
- Reprodução simultânea de várias faixas.
- Pause, seek, loop e agendamento de eventos.
- Reamostragem e seleção de dispositivo.
- Interface PyQt6.
- Análise espectral, BPM e onsets.
- Demucs, Whisper e APIs de letras.

## 3. Arquitetura

```text
src/harmoniac/
├── __main__.py          # CLI: --version, demo, play
└── audio/
    ├── __init__.py
    ├── models.py        # AudioData
    ├── signal.py        # generate_sine
    ├── wav.py           # load_wav, save_wav, AudioLoadError
    └── player.py        # BlockReader, AudioPlayer, AudioPlaybackError
```

### 3.1. Responsabilidades

| Módulo | Responsabilidade |
|---|---|
| `models.py` | Contrato de dados de áudio e validações |
| `signal.py` | Geração de sinais de teste |
| `wav.py` | Persistência em WAV |
| `player.py` | Reprodução em tempo real e leitura em blocos |
| `__main__.py` | Interface de linha de comando |

A separação mantém o modelo independente do `sounddevice` e do `soundfile`. Os
testes do modelo e do leitor de blocos não precisam de hardware.

## 4. API

### 4.1. `AudioData`

```python
@dataclass(frozen=True, slots=True)
class AudioData:
    samples: Samples  # NDArray[float32], formato (frames, canais)
    samplerate: int  # Hz
```

Invariantes verificadas em `__post_init__`:

- `samples.ndim == 2`;
- `samples.dtype == np.float32`;
- `samplerate > 0`;
- pelo menos um frame;
- pelo menos um canal.

Propriedades derivadas:

- `frames`: número de frames;
- `channels`: número de canais;
- `duration_seconds`: `frames / samplerate`.

O objeto é imutável (`frozen=True`) e usa `slots=True` para reduzir overhead.

### 4.2. `generate_sine`

```python
def generate_sine(
    frequency_hz: float,
    duration_seconds: float,
    samplerate: int,
    amplitude: float = 0.2,
    channels: int = 2,
) -> AudioData:
```

Gera:

$$
x[n] = A \sin\left(2\pi f \frac{n}{f_s}\right)
$$

com $n = 0, 1, \ldots, N-1$ e $N = \text{round}(T f_s)$.

Validações:

- `samplerate > 0`;
- $0 < f < f_s/2$ (Nyquist);
- `duration_seconds > 0`;
- $0 < A \le 1$;
- `channels > 0`;
- pelo menos um frame.

O mesmo sinal é replicado em todos os canais. Para estéreo, os dois canais são
idênticos; isso é suficiente para testar o player e o roteamento de canais.

### 4.3. WAV

```python
def load_wav(path: Path) -> AudioData:
def save_wav(path: Path, data: AudioData, *, subtype: str = "FLOAT") -> None:
```

`load_wav` usa:

```python
samples, samplerate = sf.read(path, dtype="float32", always_2d=True)
```

e converte o resultado para `float32` com `np.asarray`. Erros de leitura são
envolvidos em `AudioLoadError`.

`save_wav` usa `sf.write` com subtipo configurável. O padrão `FLOAT` preserva a
precisão interna; `PCM_16` pode ser usado para compatibilidade.

### 4.4. `BlockReader`

```python
reader = BlockReader(data.samples)
reader.fill(outdata)
reader.position
reader.finished
```

`fill` copia o próximo bloco para `outdata` e completa com zeros se o áudio
acabar. A posição avança apenas pelos frames realmente copiados. O leitor é
usado pela thread de áudio; a posição é um inteiro lido pela thread principal.

### 4.5. `AudioPlayer`

```python
player = AudioPlayer(blocksize=1024)
player.play(data)
player.wait()
player.stop()
player.is_playing
player.position_seconds
player.had_status
```

O construtor aceita `stream_factory` para injetar um stream falso nos testes.
Sem injeção, usa `sd.OutputStream`.

O callback:

```python
def callback(outdata, _frames, _time_info, status):
    if status:
        self._had_status = True

    reader.fill(outdata)
    if reader.finished:
        finished.set()
        raise sd.CallbackStop
```

O stream é criado com:

- `samplerate=data.samplerate`;
- `channels=data.channels`;
- `blocksize=self._blocksize`;
- `dtype="float32"`;
- `callback=callback`.

Se a criação ou o `start()` falhar, o stream é fechado (quando já existe) e o
erro é convertido em `AudioPlaybackError`.

`wait()` bloqueia até o evento `finished` ser sinalizado. `stop()` também
sinaliza o evento e libera o stream, permitindo interromper a reprodução.

## 5. CLI

```bash
harmoniac --version
harmoniac --help

harmoniac demo --frequency 440 --duration 3
harmoniac demo --frequency 220 --duration 2 --samplerate 48000 --channels 1

harmoniac play caminho/para/arquivo.wav
```

- `demo` gera uma senoide e a reproduz no dispositivo padrão.
- `play` carrega um WAV e o reproduz.
- Erros de áudio ou de arquivo imprimem uma mensagem e saem com código 1.
- Sem subcomando, o CLI imprime a ajuda.

A reprodução real depende de um dispositivo de saída disponível. Em ambientes
sem áudio, o comando pode falhar com `AudioPlaybackError`; os testes usam um
stream falso.

## 6. Fluxo de reprodução

```text
1. generate_sine() ou load_wav()
        ↓
2. AudioData(samples=(frames, canais), samplerate)
        ↓
3. AudioPlayer.play(data)
   ├── stop() da reprodução anterior
   ├── cria BlockReader
   ├── cria threading.Event finished
   ├── define callback
   ├── cria OutputStream
   └── stream.start()
        ↓
4. PortAudio chama callback repetidamente
   ├── reader.fill(outdata)
   ├── atualiza posição
   └── ao terminar: finished.set() + raise sd.CallbackStop
        ↓
5. AudioPlayer.wait() retorna
        ↓
6. AudioPlayer.stop()
   ├── stream.stop()
   └── stream.close()
```

## 7. Decisões de projeto

### 7.1. Callback em vez de `sd.play`

O callback dá controle sobre posição, status e término. Também é a base para o
mixer da Fase 2, que precisará somar várias fontes no mesmo bloco.

### 7.2. `float32` como formato interno

É o formato nativo do `sounddevice`, evita conversões por bloco e mantém
precisão suficiente para DSP. A conversão para `PCM_16` fica restrita à
exportação.

### 7.3. Formato `(frames, canais)`

Esse é o formato usado por `sounddevice` e `soundfile`. Ele elimina a ambiguidade
entre “número de amostras” e “número de frames” em estéreo.

### 7.4. Injeção de `stream_factory`

Permite testar `AudioPlayer` sem abrir o dispositivo de áudio. O teste fornece um
`FakeStream` que registra `start`, `stop`, `close` e expõe o callback.

### 7.5. `blocksize=1024`

A 44,1 kHz, 1024 frames correspondem a aproximadamente 23 ms. É um equilíbrio
razoável entre latência e custo de callback. O valor é configurável.

### 7.6. Exceções específicas

`AudioPlaybackError` e `AudioLoadError` separam falhas de dispositivo das falhas
de arquivo. O CLI pode tratar cada caso com uma mensagem adequada.

## 8. Testes

```text
tests/unit/
├── test_smoke.py    # versão, --version e ajuda do CLI
├── test_signal.py   # forma, amplitude, Nyquist e duração
├── test_wav.py      # roundtrip, arquivo ausente, mono e invariantes
└── test_player.py   # BlockReader, start/stop, callback e erro de start
```

Cobertura dos testes:

| Arquivo | O que verifica |
|---|---|
| `test_smoke.py` | `__version__`, `main(["--version"])`, help sem subcomando |
| `test_signal.py` | shape, dtype, sample rate, amplitude, Nyquist, duração inválida |
| `test_wav.py` | roundtrip float32, arquivo inexistente, mono, invariantes de `AudioData` |
| `test_player.py` | preenchimento/padding, silêncio após o fim, start/stop, posição, `CallbackStop`, falha de start com fechamento |

O `FakeStream` implementa `start`, `stop`, `close` e guarda o callback. O teste
de falha de start verifica que o stream é fechado e que o erro é convertido em
`AudioPlaybackError`.

## 9. Validação

Execução em 2026-10-21, com Python 3.12.3:

| Verificação | Resultado |
|---|---|
| `pytest` | **17 testes passando** |
| Cobertura total | **82%** |
| `ruff check .` | **All checks passed!** |
| `ruff format --check .` | **24 files already formatted** |
| `mypy src` | **Success: no issues found in 10 source files** |
| `harmoniac --version` | `harmoniac 0.1.0` |
| `harmoniac --help` | ajuda com `demo` e `play` |

### Versões principais instaladas

| Pacote | Versão |
|---|---|
| Python | 3.12.3 |
| numpy | 2.5.4 |
| scipy | 1.18.1 |
| librosa | 1.0.0 |
| sounddevice | 0.5.6 |
| soundfile | 0.14.0 |
| PyQt6 | 6.11.0 |
| pytest | 9.1.1 |
| pytest-cov | 7.1.0 |
| ruff | 0.17.1 |
| mypy | 2.4.0 |

A reprodução real não foi executada neste ambiente. O teste manual recomendado
é:

```bash
harmoniac demo --frequency 440 --duration 2
```

## 10. Limitações conhecidas

- **Sem reamostragem:** o sample rate do áudio precisa ser compatível com o
  dispositivo. Não há conversão automática.
- **Sem seleção de dispositivo:** o player usa o dispositivo padrão do sistema.
- **Sem mixer:** apenas uma fonte por vez.
- **Sem pause/seek/loop:** o controle é `play`, `wait` e `stop`.
- **Posição aproximada:** `position_seconds` avança por bloco e não compensa a
  latência de saída.
- **Status agregado:** `had_status` apenas indica que houve algum aviso; não
  conta underruns/overruns.
- **Sem teste com hardware:** os testes usam `FakeStream`; a reprodução real
  precisa ser validada manualmente.
- **Cobertura parcial do CLI:** os caminhos `demo` e `play` não são exercitados
  por testes automatizados porque dependem de áudio.

## 11. Próximos passos

1. Validar a reprodução real em um dispositivo de saída.
2. Iniciar a Fase 2: mixer multicanal, ganhos e Clear Tracks.
3. Adicionar seleção de dispositivo e tratamento de sample rate.
4. Evoluir o `AudioPlayer` para múltiplas fontes no mesmo callback.
5. Preparar a integração com a UI e o agendamento de eventos.
