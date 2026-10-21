# Fase 1 — Engine de Áudio

## 1. Objetivo

A Fase 1 implementa a primeira camada de áudio do Harmoniac: representar,
gerar, carregar, salvar e reproduzir áudio digital. Ela ainda não tem interface
gráfica, mixer, metrônomo ou análise musical.

Quando dizemos “engine” nesta fase, não estamos falando de um sistema completo
de produção musical. Estamos falando do conjunto mínimo de abstrações que
permite descrever um bloco de áudio, movê-lo para a saída do sistema e testar
esse caminho sem depender de hardware.

Ao final desta fase, o projeto deve ser capaz de:

- representar áudio como uma matriz `(frames, canais)` em `float32`;
- gerar uma senoide de teste;
- carregar e salvar arquivos WAV;
- reproduzir áudio com `sounddevice` usando callback;
- informar posição, término e ocorrência de underrun/overrun;
- expor tudo isso em um CLI simples.

A teoria por trás desses conceitos está em
[`docs/teoria/01-audio-digital-e-buffers.md`](../teoria/01-audio-digital-e-buffers.md).
Este documento foca nas decisões de engenharia e na API implementada.

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
- Roteiro de teste manual para validação auditiva.

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

A direção das dependências é importante:

```text
__main__ ──► signal ──► models
   │
   ├──► wav ────────► models
   └──► player ─────► models
```

`models.py` depende apenas de NumPy. Ele não importa `sounddevice`, `soundfile`
nem código de interface. Isso mantém o modelo testável, portável e independente
do dispositivo de áudio.

Os módulos de `signal`, `wav` e `player` conhecem o modelo, mas não conhecem uns
aos outros. O CLI é a camada que coordena tudo.

## 4. API

### 4.1. `AudioData`

#### O que é e por que existe

Imagine que o player recebesse apenas um array NumPy:

```python
def play(samples: np.ndarray, samplerate: int) -> None: ...
```

À primeira vista, parece simples. Na prática, essa assinatura esconde várias
perguntas:

- O array é `(frames, canais)` ou `(canais, frames)`?
- As amostras são `float32`, `float64` ou `int16`?
- O sample rate é 44.100 Hz, 48.000 Hz ou outra coisa?
- O array pode estar vazio?
- Quem garante que o sample rate é positivo?

Se cada função precisar responder a essas perguntas, a validação se espalha
pelo código. Pior: um erro de forma ou de dtype pode aparecer longe da origem,
dentro do callback de áudio, onde é difícil diagnosticar.

`AudioData` resolve isso reunindo **dados** e **metadados** em um único objeto,
validado no momento da criação. Depois que um `AudioData` existe, o restante do
código pode confiar nas suas invariantes.

Em termos práticos, `AudioData` é:

- um **objeto de valor** (_value object_): uma descrição pequena e autocontida
  de um bloco de áudio;
- um **contrato** entre quem produz áudio (`generate_sine`, `load_wav`) e quem
  consome áudio (`AudioPlayer`, futuramente o mixer e a UI);
- um lugar único para validar forma, dtype e sample rate.

Uma analogia útil: `AudioData` é como a ficha técnica de um trecho de áudio. A
ficha informa o formato, a taxa e os dados; ela não é o aparelho que reproduz o
som.

#### O que ele não faz

`AudioData` responde à pergunta “que áudio é este?”, não à pergunta “o que devo
fazer com este áudio?”.

Ele não abre dispositivo, não toca, não lê arquivo, não faz resampling e não
processa DSP. Essas responsabilidades ficam em outros módulos. Essa separação é
intencional: o modelo permanece independente do dispositivo e fácil de testar.

#### Anatomia

```python
@dataclass(frozen=True, slots=True)
class AudioData:
    samples: Samples
    samplerate: int
```

O tipo `Samples` é um alias:

```python
Samples = npt.NDArray[np.float32]
```

Ou seja, `samples` é um array NumPy de duas dimensões, com valores em `float32`.

| Membro | Tipo | Significado |
|---|---|---|
| `samples` | `NDArray[np.float32]` | Matriz `(frames, canais)` com as amostras |
| `samplerate` | `int` | Taxa de amostragem em Hz |
| `frames` | `int` (propriedade) | Quantidade de amostras por canal |
| `channels` | `int` (propriedade) | Quantidade de canais |
| `duration_seconds` | `float` (propriedade) | Duração total em segundos |

As propriedades são derivadas, não armazenadas. Isso evita inconsistência: não
é possível ter `frames` diferente de `samples.shape[0]`.

Os valores de `samples` são normalizados, em princípio, no intervalo
$[-1, 1]$. O modelo **não** valida essa faixa; ele apenas garante forma e dtype.
A limitação de amplitude é responsabilidade de quem gera o sinal
(`generate_sine`) ou de quem processa o áudio. O DAC pode clipar valores fora
da faixa.

#### Exemplo concreto

Suponha um segundo de silêncio estéreo a 44,1 kHz:

```python
import numpy as np

from harmoniac.audio.models import AudioData

samples = np.zeros((44100, 2), dtype=np.float32)
audio = AudioData(samples=samples, samplerate=44100)

print(audio.samples.shape)  # (44100, 2)
print(audio.frames)  # 44100
print(audio.channels)  # 2
print(audio.duration_seconds)  # 1.0
```

A matriz tem 44.100 linhas (frames) e 2 colunas (canais). O número total de
valores escalares é:

$$
44100 \times 2 = 88200
$$

Em `float32`, cada valor ocupa 4 bytes, então o array ocupa aproximadamente:

$$
88200 \times 4 = 352800 \text{ bytes} \approx 345 \text{ KiB}
$$

Um array 1D com 44.100 valores não diz se é mono ou se é um estéreo “achatado”.
O formato `(frames, canais)` elimina essa ambiguidade. Se tentarmos criar um
`AudioData` com um array 1D:

```python
AudioData(samples=np.zeros(44100, dtype=np.float32), samplerate=44100)
```

obtemos:

```text
ValueError: samples deve ter formato (frames, canais)
```

A forma correta para mono é:

```python
samples = np.zeros((44100, 1), dtype=np.float32)
```

E um array em `float64` também é rejeitado:

```python
AudioData(samples=np.zeros((44100, 2), dtype=np.float64), samplerate=44100)
# ValueError: samples deve ser float32
```

Esses erros acontecem cedo, no ponto de criação, e não dentro do callback de
áudio.

#### Invariantes

`AudioData` verifica cinco condições em `__post_init__`:

| Verificação | O que impede | Exemplo de entrada inválida |
|---|---|---|
| `samples.ndim == 2` | Forma ambígua ou incompatível com o stream | `np.zeros(44100)` |
| `samples.dtype == np.float32` | Conversões implícitas e DSP inconsistente | `np.zeros((100, 2), dtype=np.float64)` |
| `samplerate > 0` | Divisão por zero e stream inválido | `samplerate=0` |
| `samples.shape[0] > 0` | Buffer vazio e callback sem dados | `np.zeros((0, 2))` |
| `samples.shape[1] > 0` | Frame sem nenhum canal | `np.zeros((100, 0))` |

A ideia é **falhar cedo**. Um áudio inválido deve ser rejeitado quando é
construído, não quando já está no dispositivo de saída.

As invariantes não cobrem tudo. Elas não verificam:

- se os valores estão em $[-1, 1]$;
- se o array é contíguo em memória;
- se há `NaN` ou `Inf`;
- se o sample rate é suportado pelo dispositivo.

Essas verificações podem ser adicionadas no futuro, mas exigem uma decisão
explícita: algumas são caras, outras dependem do dispositivo e outras podem ser
responsabilidade da camada de processamento.

#### Imutabilidade e `slots`

`frozen=True` impede a reatribuição dos campos:

```python
audio.samplerate = 48000
# dataclasses.FrozenInstanceError
```

No entanto, `frozen=True` **não** torna o array NumPy imutável:

```python
audio.samples[0, 0] = 0.5  # permitido
```

Isso acontece porque o dataclass congela a referência ao array, não o conteúdo
do array. Copiar o array em toda criação de `AudioData` seria caro para áudios
longos. A convenção é tratar `audio.samples` como somente leitura.

`slots=True` reduz o overhead por instância e impede a criação de atributos
dinâmicos:

```python
audio.novo_campo = 1  # AttributeError
```

`slots` não é o mesmo que imutabilidade; são mecanismos diferentes que, juntos,
tornam o objeto mais previsível e econômico.

#### Onde ele entra no fluxo

```text
generate_sine ─┐
               ├──► AudioData ──► AudioPlayer ──► sounddevice
load_wav ──────┘
```

- `generate_sine` e `load_wav` são **produtores**: criam `AudioData`.
- `AudioPlayer` é **consumidor**: lê `data.samples` e usa `data.samplerate` e
  `data.channels` para abrir o stream.
- No futuro, o mixer e a UI também serão consumidores ou produtores de
  `AudioData`.

Esse é o principal valor do modelo: ele é o ponto de encontro entre as camadas.

#### Resumo da API

```python
AudioData(samples: Samples, samplerate: int)

audio.samples
audio.samplerate
audio.frames
audio.channels
audio.duration_seconds
```

A implementação completa está em `src/harmoniac/audio/models.py`.

### 4.2. `generate_sine`

`generate_sine` é um gerador de sinal de teste, não um sintetizador musical.
Ele produz áudio conhecido, com frequência, duração e amplitude controladas,
sem depender de arquivos externos. Isso é útil para validar o player, a leitura
em blocos e o formato `(frames, canais)`.

A fórmula é:

$$
x[n] = A \sin\left(2\pi f \frac{n}{f_s}\right)
$$

com $n = 0, 1, \ldots, N-1$ e:

$$
N = \text{round}(T f_s)
$$

onde $A$ é a amplitude, $f$ é a frequência, $f_s$ é o sample rate e $T$ é a
duração em segundos.

O termo $n/f_s$ é o tempo discreto da amostra $n$. A cada $f_s/f$ amostras, a
fase completa uma volta de $2\pi$. A 44,1 kHz, uma senoide de 440 Hz tem
aproximadamente 100,23 amostras por ciclo. Como esse número não é inteiro, o
último ciclo não termina exatamente em uma amostra; isso é normal em áudio
digital.

Validações:

| Parâmetro | Condição | Motivo |
|---|---|---|
| `samplerate` | `> 0` | Evita divisão por zero e taxa inválida |
| `frequency_hz` | $0 < f < f_s/2$ | Evita aliasing |
| `duration_seconds` | `> 0` | Evita áudio vazio ou negativo |
| `amplitude` | $0 < A \le 1$ | Evita clipping e silêncio total |
| `channels` | `> 0` | Evita frame sem canais |
| `frames` | `> 0` | Evita buffer vazio |

A validação de Nyquist é particularmente importante. Se `frequency_hz` for
maior ou igual a `samplerate / 2`, a senoide gerada não representa a frequência
pedida: ela aparece “dobrada” para uma frequência mais baixa.

Exemplo:

```python
from harmoniac.audio.signal import generate_sine

audio = generate_sine(
    frequency_hz=440.0,
    duration_seconds=1.0,
    samplerate=44100,
    amplitude=0.2,
    channels=2,
)

print(audio.samples.shape)  # (44100, 2)
print(audio.frames)  # 44100
print(audio.channels)  # 2
```

O mesmo sinal é replicado nos dois canais. Isso não cria uma imagem estéreo
“real”; serve apenas para testar o roteamento e o formato. Para pan, atrasos
entre canais ou conteúdo diferente por canal, será necessário um gerador mais
avançado.

Erros comuns:

- **Frequência acima de Nyquist:** `ValueError`. O sinal seria um alias.
- **Amplitude maior que 1:** `ValueError`. O sinal poderia clipar.
- **Duração muito curta:** se `round(duration * samplerate) == 0`, o áudio teria
  zero frames e seria rejeitado.
- **Canais zero ou negativos:** `ValueError`.
- **Sample rate zero ou negativo:** `ValueError`.

### 4.3. WAV

WAV é um contêiner do formato RIFF. Ele guarda os metadados necessários para
interpretar as amostras: número de canais, taxa de amostragem, profundidade de
bits, formato de codificação e os dados amostrados.

Na Fase 1, o WAV é usado porque, no nosso caso (PCM/FLOAT), é simples, sem perdas
e amplamente suportado. Ele não é um formato de distribuição musical eficiente,
mas é excelente para testes e para armazenar áudio intermediário.

Leitura:

```python
def load_wav(path: Path) -> AudioData:
```

A implementação usa:

```python
samples, samplerate = sf.read(path, dtype="float32", always_2d=True)
```

Pontos importantes:

- `dtype="float32"` converte PCM16 para o intervalo normalizado $[-1, 1)$;
- `always_2d=True` garante o formato `(frames, canais)` mesmo para arquivos
  mono;
- o sample rate lido do arquivo é preservado em `AudioData.samplerate`;
- erros de leitura são envolvidos em `AudioLoadError`.

Exemplo:

```python
from pathlib import Path

from harmoniac.audio.wav import load_wav

audio = load_wav(Path("entrada.wav"))
print(audio.frames, audio.channels, audio.samplerate)
```

Escrita:

```python
def save_wav(path: Path, data: AudioData, *, subtype: str = "FLOAT") -> None:
```

A implementação usa `sf.write`. O subtipo padrão é `FLOAT`, que preserva a
precisão interna. Para compatibilidade com players mais antigos, pode-se usar
`PCM_16`:

```python
from pathlib import Path

from harmoniac.audio.wav import save_wav

save_wav(Path("saida.wav"), audio, subtype="PCM_16")
```

`FLOAT` costuma ser maior e não é suportado por todos os players. `PCM_16` é
menor e mais compatível, mas introduz quantização de 16 bits. A escolha depende
do uso: processamento interno pede `FLOAT`; distribuição simples pode pedir
`PCM_16`.

Erros comuns:

- **Arquivo inexistente:** `AudioLoadError`.
- **Arquivo corrompido ou formato não suportado:** `AudioLoadError`.
- **Caminho de escrita inválido:** a exceção original do `soundfile` sobe;
  `save_wav` ainda não a envolve em uma exceção própria.
- **`PCM_16` com valores fora de $[-1, 1]$:** pode haver clipping na conversão.
- **Sample rate não suportado pelo dispositivo:** o arquivo pode ser lido, mas a
  reprodução pode falhar ao abrir o stream.

### 4.4. `BlockReader`

O callback de áudio não recebe “o áudio inteiro”. Ele recebe um buffer de
tamanho fixo e precisa preenchê-lo com o próximo trecho. `BlockReader` mantém a
posição atual e copia o trecho correto.

Separar essa responsabilidade do `AudioPlayer` tem vantagens:

- o leitor pode ser testado sem `sounddevice`;
- a lógica de cópia e padding fica em um só lugar;
- o player não precisa conhecer detalhes de indexação de arrays.

O leitor guarda a matriz completa `(frames, canais)` e uma posição inteira. O
método `fill(outdata)`:

1. descobre quantos frames o buffer de saída pede;
2. calcula quantos frames ainda restam;
3. se não resta nada, preenche tudo com zero;
4. caso contrário, copia `min(frames_pedidos, frames_restantes)`;
5. se o bloco pedido for maior que o restante, preenche o final com zero;
6. avança a posição apenas pelos frames realmente copiados.

As propriedades `position` e `finished` expõem o estado. `finished` é verdadeiro
quando a posição alcança o total de frames.

Exemplo:

```python
import numpy as np

from harmoniac.audio.player import BlockReader

samples = np.arange(5, dtype=np.float32).reshape(5, 1)
reader = BlockReader(samples)

out = np.zeros((3, 1), dtype=np.float32)

reader.fill(out)
print(out[:, 0])  # [0. 1. 2.]

reader.fill(out)
print(out[:, 0])  # [3. 4. 0.]

reader.fill(out)
print(out[:, 0])  # [0. 0. 0.]
```

No segundo bloco, só existem dois frames restantes; o terceiro é completado com
zero. No terceiro bloco, o áudio já terminou e o buffer inteiro é silêncio.

Erros comuns:

- **`outdata` com número de canais diferente de `samples`:** a atribuição falha
  ou copia dados incompatíveis.
- **Assumir que todo bloco tem `blocksize` frames:** o último bloco pode ser
  parcial; o padding existe justamente para completar.
- **Mutar `samples` durante a reprodução:** o leitor guarda uma referência, não
  uma cópia. Alterações no array podem afetar o áudio que ainda será tocado.
- **Ler `position` esperando precisão de amostra:** a posição avança por bloco.

### 4.5. `AudioPlayer`

`AudioPlayer` controla um stream de saída de áudio. Ele não é um mixer e não
mistura fontes; nesta fase, ele reproduz um `AudioData` por vez.

A escolha do callback, em vez de `sd.play`, é deliberada. `sd.play` é útil para
testes rápidos, mas esconde o stream. Com um callback explícito, o Harmoniac
consegue acompanhar a posição, detectar avisos de underrun/overrun, sinalizar o
término e preparar o terreno para o mixer da Fase 2.

O ciclo de vida é:

```text
idle ──play()──► playing ──fim do áudio──► finalizado
  ▲                  │
  └────stop()────────┘
```

- **idle:** não há stream aberto.
- **playing:** o stream foi iniciado e o callback está consumindo frames.
- **finalizado:** o áudio terminou ou `stop()` foi chamado.

`play(data)` começa chamando `stop()` para encerrar qualquer reprodução
anterior. Em seguida, cria um `BlockReader`, um `threading.Event` chamado
`finished`, define o callback, cria o `OutputStream`, inicia o stream e guarda o
estado sob um lock.

`wait()` bloqueia até o evento `finished` ser sinalizado. `stop()` também
sinaliza o evento, para e fecha o stream, e limpa o estado.

O callback roda na thread de áudio do PortAudio. Ele deve ser rápido e não pode
bloquear. No Harmoniac, ele apenas copia o próximo bloco e verifica o término:

```python
def callback(outdata, _frames, _time_info, status):
    if status:
        self._had_status = True

    reader.fill(outdata)
    if reader.finished:
        finished.set()
        raise sd.CallbackStop
```

O argumento `status` indica underrun/overrun. Nesta fase, ele apenas liga um
flag (`had_status`); não há contagem nem detalhamento. Quando o áudio termina, o
callback sinaliza o evento e levanta `sd.CallbackStop`, que é a forma que o
`sounddevice` usa para encerrar o stream a partir do próprio callback.

O callback **não deve**:

- fazer I/O (ler arquivo, acessar rede, imprimir);
- bloquear em locks, `sleep` ou operações de UI;
- alocar memória de forma pesada;
- rodar DSP complexo.

Se o callback demorar mais que o tempo do bloco, o dispositivo pode sofrer
underrun e produzir estalos.

API:

| Membro | O que faz |
|---|---|
| `AudioPlayer(blocksize=1024, stream_factory=None)` | Cria o player |
| `play(data)` | Inicia a reprodução de um `AudioData` |
| `wait()` | Bloqueia até o fim da reprodução |
| `stop()` | Interrompe e libera o stream |
| `is_playing` | Indica se há reprodução ativa |
| `position_seconds` | Posição aproximada em segundos |
| `had_status` | Indica se houve aviso de underrun/overrun |

O construtor aceita `stream_factory`. Nos testes, injetamos um `FakeStream` para
não abrir o dispositivo real. Em produção, o padrão é `sd.OutputStream`.

Há duas threads principais: a thread principal, que chama `play`, `wait` e
`stop`, e a thread de áudio, que executa o callback. O player usa um
`threading.Lock` para proteger o stream, o leitor, o sample rate e o evento
`finished`. A posição do `BlockReader` é um inteiro lido pela thread principal;
como só a thread de áudio escreve, a leitura é segura sob o GIL, mas é uma
fotografia aproximada do estado.

Erros comuns:

- **Sem dispositivo de saída:** `AudioPlaybackError`.
- **Falha ao iniciar o stream:** o stream criado é fechado e o erro vira
  `AudioPlaybackError`.
- **Callback lento:** underrun, estalos e áudio picotado.
- **Esquecer de chamar `stop()`:** o dispositivo pode ficar ocupado.
- **Sample rate não suportado:** a abertura do stream pode falhar.
- **Posição imprecisa:** `position_seconds` avança por bloco e não compensa a
  latência do dispositivo.

## 5. CLI

O CLI é a camada de conveniência. Ele não contém lógica de áudio; apenas
interpreta argumentos, chama as funções da engine e trata erros.

```bash
harmoniac --version
harmoniac --help

harmoniac demo --frequency 440 --duration 3
harmoniac demo --frequency 220 --duration 2 --samplerate 48000 --channels 1

harmoniac play caminho/para/arquivo.wav
```

| Comando | O que faz |
|---|---|
| `--version` | Imprime a versão e sai com código 0 |
| `--help` | Mostra a ajuda |
| `demo` | Gera uma senoide e a reproduz |
| `play` | Carrega um WAV e o reproduz |

Detalhes de comportamento:

- sem subcomando, o CLI imprime a ajuda;
- erros de áudio imprimem uma mensagem em `stderr` e saem com código 1;
- erros de arquivo também saem com código 1;
- parâmetros inválidos de `demo` são tratados pelo `argparse` e saem com código
  2;
- `_play` sempre chama `player.stop()` no `finally`, mesmo em caso de erro.

A função `main(argv)` aceita uma lista de argumentos, o que permite testá-la sem
depender do processo inteiro:

```python
from harmoniac.__main__ import main

main(["--version"])  # imprime a versão e levanta SystemExit(0)
```

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

O ponto importante é que o áudio nunca é copiado inteiro para o callback. O
`AudioData` permanece na memória e o `BlockReader` entrega apenas a janela
necessária para cada bloco.

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

### 7.7. Modelo separado do dispositivo

`AudioData` não conhece `sounddevice`. Isso permite testar o modelo e o leitor
de blocos sem hardware e deixa a porta aberta para outros backends de áudio no
futuro.

## 8. Testes

### 8.1. Testes automatizados

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

A estratégia é testar a maior parte da lógica sem hardware:

- funções puras (`generate_sine`, `AudioData`, `BlockReader`) têm testes
  determinísticos;
- o player é testado com um stream falso;
- a reprodução real é validada manualmente, porque depende do dispositivo.

Comando:

```bash
venv/bin/ruff format --check .
venv/bin/ruff check .
venv/bin/pytest
venv/bin/mypy src
```

### 8.2. Teste manual

O teste manual valida o que os testes automatizados não conseguem: a saída real
de áudio no dispositivo e o comportamento do CLI fora do ambiente de teste.

Pré-requisito: estar no diretório raiz do projeto, com o ambiente virtual
criado e o pacote instalado em modo editável.

1. Verifique a versão e a ajuda:

   ```bash
   venv/bin/harmoniac --version
   venv/bin/harmoniac --help
   ```

   Resultado esperado:

   - `harmoniac 0.1.0`;
   - ajuda listando os subcomandos `demo` e `play`.

2. Teste a reprodução de uma senoide curta:

   ```bash
   venv/bin/harmoniac demo --frequency 440 --duration 1 --amplitude 0.1
   ```

   Resultado esperado: um tom de 440 Hz por cerca de 1 segundo, em volume baixo,
   e código de saída 0.

3. Gere um WAV e reproduza-o:

   ```bash
   venv/bin/python - <<'PY'
   from pathlib import Path

   from harmoniac.audio.signal import generate_sine
   from harmoniac.audio.wav import save_wav

   path = Path("/tmp/harmoniac_manual.wav")
   data = generate_sine(440.0, 1.0, 44100, amplitude=0.2, channels=2)
   save_wav(path, data)
   print(path)
   PY

   venv/bin/harmoniac play /tmp/harmoniac_manual.wav
   ```

   Resultado esperado: o arquivo é criado e o mesmo tom é reproduzido.

4. Teste os caminhos de erro:

   ```bash
   venv/bin/harmoniac demo --frequency 30000 --samplerate 44100
   venv/bin/harmoniac play /tmp/arquivo-inexistente.wav
   ```

   Resultado esperado:

   - o primeiro comando falha com mensagem sobre a frequência de Nyquist e
     código de saída 2;
   - o segundo falha com mensagem de erro de arquivo e código de saída 1.

5. Registre o resultado antes de commitar ou mergear. Se algum passo falhar,
   não avance para o commit.

## 9. Validação

Execução em 2026-10-21, com Python 3.12.3:

| Verificação | Resultado |
|---|---|
| `pytest` | **17 testes passando** |
| Cobertura total | **82%** |
| `ruff check .` | **All checks passed!** |
| `ruff format --check .` | **26 files already formatted** |
| `mypy src` | **Success: no issues found in 10 source files** |
| `harmoniac --version` | `harmoniac 0.1.0` |
| `harmoniac --help` | ajuda com `demo` e `play` |

O `ruff format` também verifica blocos de código Python dentro dos arquivos
Markdown; por isso a contagem inclui a documentação.

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

A reprodução real foi validada no dispositivo padrão (`default, ALSA`) com:

```bash
harmoniac demo --frequency 440 --duration 0.5 --amplitude 0.1
harmoniac play /tmp/opencode/harmoniac_teste.wav
```

Ambos os comandos terminaram com código 0. O roteiro da seção 8.2 deve ser
executado novamente pelo usuário antes do commit e do merge.

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
- **Teste de hardware manual:** os testes automatizados usam `FakeStream`; a
  reprodução real precisa ser validada manualmente.
- **Cobertura parcial do CLI:** os caminhos `demo` e `play` não são exercitados
  por testes automatizados porque dependem de áudio.
- **`AudioData` não valida amplitude:** valores fora de $[-1, 1]$ são aceitos;
  o clipping pode acontecer no DAC.
- **`AudioData` não copia o array:** o objeto é congelado, mas o conteúdo de
  `samples` continua mutável. A convenção é tratar o array como somente leitura.
- **`save_wav` não envolve erros de escrita:** falhas de disco ou caminho
  inválido sobem como exceções do `soundfile`.
- **Sem verificação de contiguidade:** arrays não contíguos podem funcionar ou
  falhar dependendo do backend; não há checagem explícita.

## 11. Próximos passos

1. Adicionar um teste de integração opcional, executado apenas quando houver
   dispositivo de áudio disponível.
2. Iniciar a Fase 2: mixer multicanal, ganhos e Clear Tracks.
3. Adicionar seleção de dispositivo e tratamento de sample rate.
4. Evoluir o `AudioPlayer` para múltiplas fontes no mesmo callback.
5. Preparar a integração com a UI e o agendamento de eventos.
