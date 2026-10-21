# Documento de Arquitetura e Especificação Técnica: Harmoniac

## 1. Visão Geral, Problema e Objetivos do Projeto

### O Problema
Músicos estudantes frequentemente utilizam plataformas de cifras (como Cifra Club e Ultimate Guitar) que apresentam falhas crônicas para o estudo aprofundado:
* **Falta de Sincronia Real:** A rolagem é linear ("burra"), ignorando a dinâmica temporal (BPM) da música, fazendo com que o músico se perca facilmente.
* **Poluição Sonora:** Dificuldade em isolar instrumentos específicos devido à mixagem densa.
* **Falta de Referência de Tempo:** Iniciantes têm dificuldade em saber o milissegundo exato de mudar a posição da mão esquerda.

### O Objetivo e a "Killer Feature"
Desenvolver o **Harmoniac**, um software desktop open-source para treinamento musical de precisão. A interface final será um **"Cifra Club Inteligente"**: a letra da música e os acordes posicionados acima das sílabas correspondentes brilharão na tela sincronizados via Inteligência Artificial, utilizando **Sincronia Orientada a Eventos**.

**Novidade (Fallback de Letras):** O sistema será resiliente. Caso a música não possua letra encontrada nas APIs, ou o usuário deseje focar puramente na harmonia, haverá uma opção para **ocultar as letras**. Neste modo, a interface exibirá apenas a grade de acordes brilhando no exato momento da troca, funcionando como uma partitura rítmica visual.

## 2. Fundamentação Teórica e Complexidade (Conexão Acadêmica ES879)

Este projeto eleva a complexidade de um simples player de áudio para um cenário de **Engenharia de Software do Mundo Real**, aplicando diretamente os conceitos de Processamento Digital de Sinais (DSP):

* **Sistemas de Aquisição de Dados (Conversão D/A e Nyquist):** Respeitando o Teorema de Nyquist, operaremos na taxa padrão de $F_s = 44100$ Hz para garantir a fidelidade espectral sem *aliasing*. O uso do `sounddevice` e matrizes NumPy aplicará conceitos práticos de buffers (*blocksize*) e *Sample & Hold* para evitar underruns.
* **Sinais e Sistemas Discretos (Operações no Tempo):** O Mixer Multicanal implementará somadores digitais clássicos: $y_{mix}[n] = \sum (G_i \cdot x_i[n])$, onde $G$ é o valor (ganho) do slider de volume na interface.
* **Análise Espectral (FFT, Leakage e Janelamento):** A detecção de *onsets* e cálculo de BPM pelo `librosa` utilizará a Transformada de Fourier Discreta (DFT/STFT) com janelamentos (ex: Hanning/Tukey) para mitigar o *Leakage* espectral ao isolar ataques de bateria.
* **Sistemas LTI e Filtros:** A função de mudar o andamento (Time-Stretching) sem alterar o tom implementará técnicas de *Phase Vocoder* (manipulação de fase no domínio da frequência), demonstrando convolução avançada e processamento de matrizes.

### 2.1. Observação Importante - Notas de Aula

Eu tenho algumas anotações de aula, que fiz durante a disciplina de Sistema de Aquisição de Dados em minha graduação. Esse projeto busca colocar em prática os conceitos que eu aprendi durante essa disciplina. Sei que a complexidade do projeto é bem superior às minhas anotações, mas gostaria de realizar esse projeto e compreendendo os conceitos teóricos de matemática, física, computação e engenharia aprendidos durante a graduação. Por isso, eu gostaria que, no decorrer do projeto, você criasse e mantesse uma documentação, organizada por várias notas, explicando os conceitos teóricos, destrinchando partes relevantes das documentações das bibliotecas utilizadas. Sei que minhas notas não cobrem todo o conteúdo e, para contornar isso, as notas notas criadas devem cobrir esse conteúdo. Para equações matemáticas, utilize o LaTEX e Markdown. As notas de aula devem estar em arquivos .md. 

Não quero apenas escrever um prompt simples para seguirmos as etapas do projeto e ficar clicando Enter para dar permissão enquanto você faz todo o projeto. Dessa forma, quero participar do projeto e entender claramente o que tá acontecendo, por quê fazer de tal forma, etc.

## 3. Stack Tecnológico

Aqui, tenho listado ferramentas que não foram escolhidas por mim, pois não sabia como iniciar o projeto, mas por uma resposta gerada por Inteligência Artificial para dar um rumo ao projeto. Conforme formos executando o projeto, você pode me fazer perguntas para que decidimos se mantenhamos essa ferramenta ou utilizamos outra.

* **Core / DSP:** `Python 3.10+`, `numpy`, `scipy`.
* **Análise Musical:** `librosa` (BPM e onsets).
* **Audio Engine:** `sounddevice` (baixa latência de I/O).
* **Inteligência Artificial (Offline):**
  * `Demucs` (Meta) para separação de hastes (stems) de áudio.
  * `Whisper` (OpenAI) para timestamping e alinhamento forçado (Karaokê).
* **Interface Gráfica (UI):** `PyQt6` (Multithreading robusto com `QThread`).
* **APIs de Letras:** `LyricsGenius` ou `Vagalume API`.

## 4. Arquitetura do Sistema e Fluxo de Dados (MVC Expandido)

O projeto é dividido em três módulos assíncronos:

### A. Módulo de Pré-Processamento (DSP & AI Analyzer) - *Offline*
1. **Separação (Demucs):** Transforma o sinal $x[n]$ em 4 matrizes distintas (Voz, Bateria, Baixo, Outros).
2. **Alinhamento e Extração:** Busca a letra. Se encontrada, o Whisper cruza o áudio isolado com o texto gerando timestamps. Se não encontrada, cria uma grade baseada apenas nas batidas e trocas de acordes.
3. **BPM:** O `librosa` calcula o compasso.

### B. Módulo de Reprodução (Audio Player Engine) - *Tempo Real*
1. **Mixer Matricial:** Lê e soma as matrizes simultaneamente.
2. **Sistema Clear Tracks (Anti-Vazamento):** Botão/função vital que limpa os buffers e zera variáveis globais ao trocar de música, impedindo sobreposição acidental de matrizes na memória.
3. **Time-Stretching e BPM Dinâmico:** Reamostragem (x0.5, x1.0, x2.0).
4. **Metrônomo Injetor:** Soma o impulso digital $\delta[n-k]$ (beep) nos instantes calculados.

### C. Módulo de Interface Gráfica (UI)
Um timer (`QTimer`) consulta o relógio do Audio Engine a $\approx 60$ FPS. Compara o tempo atual com o JSON Mestre e aplica QSS (CSS) para iluminar sílabas e acordes.

## 5. Modelagem de Dados (JSON Mestre)

```json
{
  "id_musica": "uuid-v4",
  "titulo": "Nome da Música",
  "bpm_original": 120.0,
  "exibir_letra": true,
  "eventos_temporais": [
    { "timestamp_ms": 1500, "tipo": "metronomo", "valor": "beat_1" },
    { "timestamp_ms": 1500, "tipo": "acorde", "valor": "Am7", "duracao_ms": 2000 },
    { "timestamp_ms": 1520, "tipo": "letra", "valor": "Yester...", "duracao_ms": 480 }
  ]
}
```

## 6. Estrutura de Diretórios e Git Flow

Usaremos commits convencionais (ex: `feat:`, `fix:`) e o modelo Git Flow: `main`, `develop` e `feature/*`.

```text
harmoniac/
├── docs/                     # Documentação do projeto
├── src/
│   ├── core/                 # JSON Models, Data Classes
│   ├── dsp/                  # DSP Analyzer, BPM, Whisper Sync
│   ├── audio/                # Player, Mixer, Clear Tracks logic
│   └── ui/                   # Telas PyQt6
├── assets/                   # Ícones e bips (.wav)
├── data/                     # Workspace local (Stems)
└── requirements.txt
```

## 7. Roadmap de Implementação (Fases)

* **Fase 1: Fundação do Áudio LTI (Engine Base):** Tocar um array NumPy (`WAV`) genérico usando `sounddevice` sem travar o terminal.
* **Fase 2: Mixer Multicanal e Botão Clear:** Somar matrizes de áudio em tempo real com controle escalar de volume. **Requisito:** Implementar a lógica de "Limpar Faixas" para gerenciar a troca segura de músicas.
* **Fase 3: UI Básica e Multithreading:** Conectar a lógica no PyQt6 usando `QThread`.
* **Fase 4: Coração Analítico (BPM e Metrônomo):** Usar `librosa` para extrair BPM. **Requisito:** Botões "BPM x0.5" e "BPM x2" para corrigir oitavas rítmicas.
* **Fase 5: Separação IA (Demucs):** Botão "Analisar Música" para separar os caules offline e salvar na pasta `data/`.
* **Fase 6: Motor de Karaokê e Acordes (Whisper):** API de letras e alinhamento forçado. **Requisito:** Toggle para "Ocultar Letras", renderizando apenas a linha do tempo de acordes.
* **Fase 7: Renderização Visual "Cifra Inteligente":** Painel visual reativo que lê o JSON e acende os elementos sincronizados no tempo real.

## 8. Documentação do Projeto

Para cada etapa do código, deve ser criado (ou alterado) um arquivo de documentação referente a alteração realizada. Nessa documentação, deve estar sendo explicada cada arquivo .py (ou outros formatos) criado, juntamente com suas classes, métodos, funções, variáveis e trechos de código, pois o projeto é ambicioso e mostra-se fácil de se perder em meio a tantos arquivos. Portanto, a documentação deve ser clara, explicativa, didática e completa. Essa não é a mesma documentação solicitada no item 2.1, e portanto podem ficar em pastas de documentação separadas. Os arquivos devem estar em .md.

## 9. Boas práticas de programação

O projeto deve estar nas boas práticas de programação e bem arquitetado. Deve estar padroniazado e de fácil utilização.

O projeto deve estar devidamente versionado no GitHub, com as branches e commits corretas e padronizadas.