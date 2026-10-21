# Harmoniac

Treinador musical de precisão com sincronização orientada a eventos. O Harmoniac
exibe letra e acordes alinhados ao áudio e acende cada evento no instante exato da
música, funcionando como um "Cifra Club inteligente".

> **Status:** Fase 1 — engine de áudio. Reprodução, geração de senoide e leitura
> de WAV funcionam; ainda não há UI, mixer ou IA implementados.

## Stack

- Python 3.10+
- NumPy, SciPy e librosa (DSP e análise musical)
- sounddevice e soundfile (reprodução e leitura/escrita de WAV)
- PyQt6 (interface gráfica)
- Demucs e Whisper (separação de stems e alinhamento de letras)
- LyricsGenius / Vagalume (obtenção de letras)

## Estrutura

```text
src/harmoniac/
├── core/   # Modelos, contratos e estruturas de dados
├── dsp/    # Análise e processamento de sinais
├── audio/  # Motor de reprodução e mixagem
└── ui/     # Interface PyQt6
```

## Requisitos

- Python 3.10 ou superior
- `pip` e `venv` (ou `uv`, opcional)

## Instalação

### Com venv + pip

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### Com uv (opcional)

```bash
uv sync --extra dev
```

O `pyproject.toml` é a fonte única de verdade das dependências. Não utilizamos
`requirements.txt`.

## Uso rápido

```bash
harmoniac --version
harmoniac demo --frequency 440 --duration 3
harmoniac play caminho/para/arquivo.wav
```

`demo` gera uma senoide e a reproduz no dispositivo padrão. `play` carrega um
arquivo WAV e o reproduz. A reprodução depende de uma saída de áudio disponível.

## Testes e qualidade

```bash
pytest
ruff check .
ruff format --check .
mypy src
```

## Roadmap

1. Fundação do projeto (Fase 0) — concluída
2. Engine de áudio LTI (Fase 1) — concluída
3. Mixer multicanal e Clear Tracks
4. UI básica e multithreading
5. BPM e metrônomo
6. Separação com Demucs
7. Karaokê, acordes e renderização visual

## Documentação

- `docs/teoria/` — notas teóricas didáticas (Markdown/LaTeX)
- `docs/engenharia/` — documentação de código e decisões técnicas
- `docs/decisoes/` — ADRs (Architecture Decision Records)

## Licença

GPL-3.0-or-later. Consulte `LICENSE`.
