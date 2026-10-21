# Áudio Digital e Buffers

## 1. Objetivo

Esta nota conecta os conceitos de aquisição de dados e sistemas discretos da
disciplina ES879 à implementação da Fase 1 do Harmoniac. O foco é entender:

- como uma onda sonora contínua se transforma em uma sequência de números;
- por que o áudio é processado em blocos, e não amostra por amostra;
- como o `sounddevice` entrega esses blocos ao código;
- como o formato WAV representa o áudio em disco.

Ao final, o leitor deve conseguir olhar para `harmoniac.audio` e reconhecer cada
conceito teórico no código.

## 2. A cadeia do áudio digital

O som é uma variação de pressão no ar. Para processá-lo em um computador,
precisamos convertê-lo em um sinal elétrico e depois em números:

```text
pressão do ar → microfone → tensão elétrica → ADC → amostras digitais
                                                      │
alto-falante ← tensão elétrica ← DAC ← amostras digitais
```

O **ADC** (Analog-to-Digital Converter) faz duas operações principais:

1. **amostragem** no tempo (transforma tempo contínuo em tempo discreto);
2. **quantização** na amplitude (transforma amplitude contínua em níveis
   discretos).

O **DAC** (Digital-to-Analog Converter) faz o caminho inverso: recebe amostras e
reconstrói uma tensão contínua. No Harmoniac, o caminho de saída é feito pelo
`sounddevice`, que conversa com a API de áudio do sistema operacional
(PortAudio).

### 2.1. Do mundo físico ao `AudioData`

A cadeia acima termina em “amostras digitais”. No software, precisamos de uma
estrutura que diga não só quais são as amostras, mas também como interpretá-las.
É aí que entra o `AudioData`.

Um `AudioData` guarda:

- uma matriz de amostras, no formato `(frames, canais)`;
- a taxa de amostragem usada para gerar ou ler essas amostras.

Sem a taxa de amostragem, a sequência de números é ambígua: os mesmos 44.100
valores podem representar 1 segundo a 44,1 kHz, 0,919 segundo a 48 kHz ou
2 segundos a 22,05 kHz. O `AudioData` amarra os dois dados, para que essa
interpretação não se perca.

Em outras palavras:

```text
som físico → ADC → amostras + sample rate → AudioData
```

A teoria desta nota explica **o que os números significam**. O modelo
`AudioData` explica **como esses números e seu contexto viajam juntos pelo
código**.

## 3. Amostragem e o teorema de Nyquist

Um sinal contínuo $x(t)$ é amostrado em intervalos regulares $T_s$:

$$
x[n] = x(nT_s), \qquad T_s = \frac{1}{f_s}
$$

onde:

- $f_s$ é a **taxa de amostragem** (_sample rate_), em Hz;
- $T_s$ é o **período de amostragem**, em segundos;
- $n$ é o índice da amostra.

A 44,1 kHz, temos uma amostra a cada:

$$
T_s = \frac{1}{44100} \approx 22{,}68\ \mu s
$$

O **teorema de Nyquist** diz que, para reconstruir um sinal sem ambiguidade, a
taxa de amostragem precisa ser maior que o dobro da maior frequência presente
no sinal:

$$
f_s > 2 f_{\max}
$$

A frequência $f_s/2$ é chamada de **frequência de Nyquist**. Em 44,1 kHz, ela é
22,05 kHz.

### 3.1. Aliasing

Se o sinal tiver componentes acima de $f_s/2$, elas se dobram para frequências
mais baixas. Isso é o **aliasing**. Exemplo: uma senoide de 30 kHz amostrada a
44,1 kHz aparece como se fosse de:

$$
|30{,}000 - 44{,}100| = 14{,}100\ \text{Hz}
$$

O ouvido humano não escuta 30 kHz, mas escuta o alias de 14,1 kHz. Por isso,
antes do ADC existe um **filtro anti-aliasing** que remove as componentes acima
de $f_s/2$.

No código, `generate_sine` rejeita frequências que não estejam estritamente
abaixo de `samplerate / 2`:

```python
if not 0 < frequency_hz < samplerate / 2:
    raise ValueError("frequency_hz deve ficar entre 0 e a frequência de Nyquist")
```

Essa validação evita gerar um sinal que já nasce com aliasing.

### 3.2. Sample rate no Harmoniac

A Fase 1 usa 44,1 kHz como padrão, mas o sample rate é sempre um parâmetro
explícito em `AudioData`. O player abre o stream com o mesmo sample rate do
áudio carregado. Ainda não há reamostragem: se o dispositivo não suportar a
taxa pedida, a abertura do stream pode falhar.

## 4. Quantização

Depois da amostragem no tempo, a amplitude também precisa ser discretizada. Um
ADC de $N$ bits produz $2^N$ níveis. Para um sinal senoidal de amplitude
máxima, a relação sinal-ruído de quantização é aproximadamente:

$$
\text{SNR}_{\text{dB}} \approx 6{,}02N + 1{,}76
$$

Assim:

| Bits | Níveis | SNR aproximada |
|---:|---:|---:|
| 8 | 256 | 50 dB |
| 16 | 65.536 | 98 dB |
| 24 | 16.777.216 | 146 dB |

O WAV `PCM_16` usa inteiros de 16 bits. O `soundfile`, ao ler com
`dtype="float32"`, converte esses inteiros para o intervalo normalizado
$[-1, 1)$. O Harmoniac usa `float32` internamente porque:

- é o formato nativo do `sounddevice`;
- facilita o processamento DSP (ganhos, mixagem, filtros);
- evita converter de inteiro para float a cada bloco.

O `float32` tem 24 bits de significando, o que dá uma precisão efetiva próxima
de 24 bits para valores normalizados. Valores fora de $[-1, 1]$ podem ser
clipados pelo DAC. Por isso, `generate_sine` limita a amplitude a $0 < a \le 1$.

## 5. Buffers, frames e blocos

Seria caro pedir ao sistema operacional uma interrupção por amostra. Em vez
disso, o áudio é transferido em **blocos** (_buffers_). Cada bloco contém um
número fixo de **frames**.

Em áudio digital, um **frame** é o conjunto de uma amostra por canal:

- mono: 1 amostra por frame;
- estéreo: 2 amostras por frame (esquerda e direita);
- 5.1: 6 amostras por frame.

Um bloco estéreo de 1024 frames contém:

$$
1024 \times 2 = 2048 \text{ amostras}
$$

Em `float32`, isso ocupa:

$$
2048 \times 4 = 8192 \text{ bytes} = 8 \text{ KiB}
$$

O tempo que um bloco leva para tocar é:

$$
t_{\text{bloco}} = \frac{\text{blocksize}}{f_s}
$$

| Blocksize | Latência a 44,1 kHz |
|---:|---:|
| 256 | 5,8 ms |
| 512 | 11,6 ms |
| 1024 | 23,2 ms |
| 2048 | 46,4 ms |

Blocos menores reduzem a latência, mas aumentam a frequência de callbacks e o
risco de **underrun**. Blocos maiores são mais eficientes, mas aumentam a
latência. A Fase 1 usa 1024 frames como padrão.

### 5.1. Um exemplo concreto: 4 frames estéreo

Considere quatro frames de áudio estéreo. Cada frame tem uma amostra da esquerda
(L) e uma da direita (R):

```text
frame 0: [L0, R0]
frame 1: [L1, R1]
frame 2: [L2, R2]
frame 3: [L3, R3]
```

Como matriz `(frames, canais)`, isso fica:

```text
[[L0, R0],
 [L1, R1],
 [L2, R2],
 [L3, R3]]
```

A forma é `(4, 2)`:

- 4 frames;
- 2 canais;
- 8 valores escalares.

Se alguém dissesse apenas “oito amostras”, não saberíamos se são quatro frames
estéreo, oito frames mono ou outra combinação. A noção de frame resolve essa
ambiguidade.

### 5.2. Underrun e overrun

- **Underrun** (_underrun_): o dispositivo precisou de dados e o buffer estava
  vazio. O resultado típico é um estalo ou silêncio.
- **Overrun**: o buffer encheu porque o produtor foi mais rápido que o
  consumidor.

O callback do `sounddevice` recebe um argumento `status` que indica esses
eventos. O `AudioPlayer` registra a ocorrência em `had_status`, mas ainda não
detalha quantos underruns ocorreram.

### 5.3. Buffer no código

`AudioData.samples` é uma matriz com formato `(frames, canais)`:

```python
data.samples.shape  # (frames, channels)
data.frames  # número de frames
data.channels  # número de canais
```

O `BlockReader` mantém uma posição inteira e preenche o buffer de saída:

```python
reader.fill(outdata)
```

Se o bloco pedido for maior que o restante do áudio, o leitor copia o que existe
e completa o resto com zeros. Isso evita estalos no final e permite que o
callback sempre receba um buffer cheio.

### 5.4. Por que sample rate e samples andam juntos

A sequência de amostras, sozinha, não determina a duração nem a frequência do
som. O sample rate é parte da interpretação.

Suponha um array com 44.100 amostras:

- a 44.100 Hz, ele dura 1 segundo;
- a 48.000 Hz, ele dura aproximadamente 0,919 segundo;
- a 22.050 Hz, ele dura 2 segundos.

O mesmo acontece com a frequência percebida. Uma senoide gerada para 440 Hz a
44.100 Hz, se reproduzida a 48.000 Hz sem reamostragem, soa mais aguda, porque
o mesmo padrão de amostras passa mais rápido pelo DAC.

Por isso, `AudioData` carrega `samples` e `samplerate` juntos. O player abre o
stream com o sample rate declarado; se o dispositivo não suportar essa taxa, a
abertura pode falhar. Ainda não há reamostragem automática.

### 5.5. O que acontece se frames e amostras forem confundidos

Em mono, frames e amostras têm o mesmo número. Em estéreo, não:

```text
1024 frames estéreo = 1024 × 2 = 2048 amostras
```

Se um buffer estéreo de 1024 frames for tratado como um array 1D de 2048
amostras, o código perde a noção de canal. Se for tratado como `(2, 1024)`, a
orientação está invertida: o player espera `(frames, canais)`, não
`(canais, frames)`.

O resultado pode ser:

- erro de forma no `AudioData`;
- áudio tocado no canal errado;
- apenas metade do áudio reproduzida;
- estalos ou silêncio.

Por isso o formato `(frames, canais)` é fixo no modelo e validado na criação.

### 5.6. O contrato `AudioData`

Do ponto de vista teórico, `AudioData` é um contrato com cinco garantias:

1. as amostras estão em `float32`;
2. a matriz tem duas dimensões, no formato `(frames, canais)`;
3. há pelo menos um frame;
4. há pelo menos um canal;
5. o sample rate é positivo.

Quem recebe um `AudioData` não precisa verificar isso de novo. Quem constrói
precisa fornecer dados válidos; caso contrário, recebe `ValueError` na hora.

O objeto é congelado (`frozen=True`), mas o array NumPy interno continua
mutável. A convenção é não alterar `audio.samples` depois da criação. Essa
distinção é importante: congelar o dataclass não congela o conteúdo do array.

## 6. O callback de áudio

O `sounddevice` usa o modelo de **callback**: o PortAudio chama uma função
Python sempre que precisa de um novo bloco. Essa função roda em uma thread de
áudio de alta prioridade, separada da thread principal.

O callback tem uma responsabilidade simples e crítica: preencher `outdata`
rapidamente. Ele **não deve**:

- fazer I/O (ler arquivo, acessar rede, imprimir);
- bloquear em locks, `sleep` ou operações de UI;
- alocar memória de forma pesada;
- rodar DSP complexo.

No Harmoniac, o callback apenas copia o próximo bloco e sinaliza o final:

```python
def callback(outdata, _frames, _time_info, status):
    if status:
        self._had_status = True

    reader.fill(outdata)
    if reader.finished:
        finished.set()
        raise sd.CallbackStop
```

O fluxo completo é:

```text
thread principal                    thread de áudio (PortAudio)
────────────────                    ────────────────────────────
AudioPlayer.play(data)
  cria BlockReader
  cria Event finished
  cria OutputStream(callback)
  stream.start()  ────────────────►  callback(outdata, ...)
                                      reader.fill(outdata)
                                      se terminou:
                                        finished.set()
                                        raise CallbackStop
AudioPlayer.wait()
  finished.wait()  ◄───────────────  (evento sinalizado)
AudioPlayer.stop()
  stream.stop()
  stream.close()
```

### 6.1. Por que não usar `sd.play`?

`sd.play` é ótimo para testes rápidos, mas esconde o controle do stream. Com um
callback explícito, o Harmoniac consegue:

- saber a posição atual da reprodução;
- detectar underruns/overruns;
- no futuro, mixar várias faixas no mesmo callback;
- sincronizar eventos visuais com o áudio.

### 6.2. Posição e latência

`AudioPlayer.position_seconds` calcula:

$$
\text{posição} = \frac{\text{frames consumidos}}{f_s}
$$

A posição é atualizada a cada bloco, não a cada amostra. Além disso, ela não
compensa a latência do dispositivo. Para sincronização visual fina, será
necessário considerar a latência de saída e o timestamp dos eventos.

## 7. WAV

O formato WAV é um contêiner RIFF. Ele guarda:

- o número de canais;
- a taxa de amostragem;
- a profundidade de bits;
- o formato de codificação (PCM inteiro ou float);
- os dados amostrados.

O Harmoniac usa `soundfile` para ler e escrever:

```python
samples, samplerate = sf.read(path, dtype="float32", always_2d=True)
sf.write(path, data.samples, data.samplerate, subtype="FLOAT")
```

Detalhes importantes:

- `always_2d=True` garante o formato `(frames, canais)` mesmo para arquivos mono;
- `dtype="float32"` converte PCM16 para $[-1, 1)$;
- o subtipo padrão da Fase 1 é `FLOAT`; para compatibilidade com players
  antigos, pode-se usar `PCM_16`;
- `sf.read` lança `RuntimeError`/`LibsndfileError` para arquivos inválidos;
  `load_wav` envolve isso em `AudioLoadError`.

## 8. Mapa teoria → código

| Conceito | Onde aparece |
|---|---|
| Taxa de amostragem | `AudioData.samplerate`, `generate_sine(samplerate=...)` |
| Período de amostragem | `time = np.arange(frames) / samplerate` |
| Nyquist e aliasing | validação de `frequency_hz` em `generate_sine` |
| Quantização | amostras `float32` normalizadas; `save_wav(subtype=...)` |
| Frame e canal | `AudioData.samples.shape == (frames, channels)` |
| Contrato de áudio | forma, dtype e sample rate juntos em `AudioData` |
| Buffer/bloco | `BlockReader.fill`, `AudioPlayer(blocksize=1024)` |
| Callback | função interna de `AudioPlayer.play` |
| Underrun/overrun | `AudioPlayer.had_status` |
| Fim do stream | `sd.CallbackStop` e `threading.Event` |
| WAV | `load_wav`, `save_wav`, `AudioLoadError` |

## 9. Erros comuns

1. **Confundir amostras com frames.** Em estéreo, 1024 frames são 2048
   amostras. O formato do Harmoniac é sempre `(frames, canais)`.
2. **Passar um array 1D para o player.** `AudioData` rejeita arrays que não
   tenham duas dimensões.
3. **Usar sample rate diferente do dispositivo.** O stream é aberto com o
   sample rate do áudio; não há reamostragem automática.
4. **Gerar frequência acima de Nyquist.** O resultado será um alias, não a
   frequência desejada.
5. **Passar de $[-1, 1]$.** O DAC pode clipar; mantenha amplitudes abaixo de 1
   e deixe headroom.
6. **Fazer trabalho pesado no callback.** Isso causa underruns e estalos.
7. **Esquecer de fechar o stream.** Use `stop()`; o player fecha o stream e
   libera o dispositivo.
8. **Achar que a posição é sample-accurate.** Ela avança em blocos e não
   compensa latência.
9. **Salvar tudo como `PCM_16` sem necessidade.** Para processamento interno,
   `FLOAT` preserva melhor a precisão; para distribuição, `PCM_16` é mais
   compatível.

## 10. Perguntas para fixar

1. Por que 44.100 amostras não são suficientes para saber a duração do áudio?
2. Em um bloco estéreo de 512 frames, quantas amostras escalares existem?
3. O que acontece com uma senoide de 30 kHz amostrada a 44,1 kHz?
4. Por que `AudioData` exige `float32`?
5. Qual é a diferença entre `frames` e `channels`?
6. Por que o callback não pode fazer I/O?
7. O que é underrun e como o player registra isso?
8. O que `frozen=True` garante e o que não garante?

## 11. Checklist

- [ ] A frequência está abaixo de `samplerate / 2`?
- [ ] As amostras estão em `float32` e no formato `(frames, canais)`?
- [ ] A amplitude está dentro de $[-1, 1]$?
- [ ] O blocksize foi escolhido considerando latência e CPU?
- [ ] O callback evita I/O, UI e bloqueios?
- [ ] O stream é fechado ao final?
- [ ] O teste usa um stream falso quando não há hardware?
- [ ] A reprodução real foi testada no dispositivo de saída?
