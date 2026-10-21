# Mapa Teoria → Código

## Objetivo

Este documento conecta as notas da disciplina ES879 aos módulos do Harmoniac.
Ele serve como bússola: antes de implementar cada parte, consultamos a teoria
correspondente e registramos, em novas notas, o que foi aprendido.

## Como usar

1. Localize o módulo que será implementado.
2. Leia os conceitos da nota indicada.
3. Registre, em `docs/teoria/`, os detalhes que não estão nas notas originais.
4. Só então implemente, com a explicação do "porquê" na documentação de engenharia.

## Notas ES879 e módulos

| Nota | Conceitos principais | Módulos do Harmoniac | Onde entra na prática |
|---|---|---|---|
| ES879 (1) | Aquisição, amostragem, Nyquist, quantização, S/H, D/A | `audio`, `core` | Taxa de 44,1 kHz, buffers, latência, underruns, saída de áudio |
| ES879 (2) | Sinais discretos, LTI, convolução, correlação, equações a diferenças | `audio`, `dsp` | Mixer como soma ponderada, delays, detecção de onsets, metrônomo como impulso |
| ES879 (3) | Transformada Z, ROC, polos/zeros, estabilidade, Z inversa | `dsp`, `audio` | Análise e projeto de filtros, estabilidade, resposta de sistemas |
| ES879 (4) | Fourier, Parseval, DTFT, resposta em frequência, filtros, deconvolução | `dsp` | Análise espectral, EQ, separação, phase vocoder, inversão |
| ES879 (5) | DFT/IDFT, resolução, zero padding, FFT, leakage, janelamento, convolução circular | `dsp` | STFT para BPM/onsets, escolha de janelas, frames/hop, processamento em blocos |

## Notas complementares

- [01 — Áudio Digital e Buffers](01-audio-digital-e-buffers.md): amostragem,
  quantização, frames, buffers, callback do `sounddevice` e formato WAV. Cobre
  a lacuna de callbacks de áudio, buffers e underruns.

## Lacunas que precisamos cobrir

As notas são a base, mas não cobrem todos os tópicos necessários. As novas notas
de `docs/teoria/` devem explicar, no mínimo:

- STFT (Short-Time Fourier Transform) e espectrograma;
- Mel spectrogram e escala mel;
- detecção de onsets e beat tracking;
- Phase Vocoder e time-stretching sem alteração de tom;
- PSOLA e alternativas de time-stretch;
- HPSS (Harmonic-Percussive Source Separation);
- alinhamento forçado (forced alignment) com Whisper;
- arquitetura do Demucs e separação de stems;
- ~~callbacks de áudio, buffers e underruns com `sounddevice`~~ (coberto na
  nota 01);
- `QThread`, sinais/slots e timers no PyQt6;
- reamostragem e filtros anti-aliasing;
- janelamento e leakage na prática.

## Trilha sugerida

1. **Fase 0:** empacotamento, estrutura e convenções.
2. **Fase 1:** revisar ES879 (1) e (2); buffers e reprodução com `sounddevice`
   (concluída; ver nota 01).
3. **Fase 2:** revisar ES879 (2); mixer, ganhos e Clear Tracks.
4. **Fase 3:** estudar `QThread`, sinais/slots e ciclo de vida da UI.
5. **Fase 4:** revisar ES879 (4) e (5); STFT, onsets e BPM com librosa.
6. **Fase 5:** estudar Demucs, PyTorch e separação de fontes.
7. **Fase 6:** estudar Whisper, alinhamento forçado e APIs de letras.
8. **Fase 7:** integrar eventos, QSS e renderização em tempo real.

## Regra de documentação

Cada nova nota deve responder:

- Qual é o conceito?
- Por que ele é necessário no Harmoniac?
- Como ele aparece no código?
- Quais são as limitações e os erros comuns?
