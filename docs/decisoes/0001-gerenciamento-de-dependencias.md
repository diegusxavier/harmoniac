# ADR 0001 — Gerenciamento de dependências com `pyproject.toml`

- **Status:** aceita
- **Data:** 2026-10-21
- **Decisores:** projeto Harmoniac

## Contexto

O projeto precisa declarar dependências, metadados, entry points e configuração
de ferramentas de forma padronizada. A especificação inicial citava
`requirements.txt`, mas esse formato não descreve metadados do pacote, extras
opcionais nem configuração de build. Além disso, o projeto usa bibliotecas
pesadas de IA (Demucs e Whisper) que não devem ser instaladas por padrão.

## Decisão

Adotar `pyproject.toml` como fonte única de verdade, seguindo a PEP 621, com
`hatchling` como build backend. As dependências são divididas em:

- `dependencies`: stack principal (NumPy, SciPy, librosa, sounddevice, PyQt6);
- `dev`: pytest, pytest-cov, ruff e mypy;
- `ai`: Demucs e Whisper (instalação opcional);
- `lyrics`: LyricsGenius e requests (instalação opcional).

O ambiente local da Fase 0 é criado com `python -m venv` + `pip`. O `uv` fica
como alternativa opcional para o futuro; se for adotado, o `uv.lock` será
versionado.

## Consequências

- Não haverá `requirements.txt`.
- `pip install -e ".[dev]"` instala o pacote em modo editável com as ferramentas
  de desenvolvimento.
- As dependências de IA não são instaladas por padrão, evitando downloads e uso
  de disco desnecessários nesta fase.
- A instalação não é totalmente reproduzível sem um lockfile. Se isso se tornar
  um problema, adotaremos `uv` e versionaremos o `uv.lock`.

## Alternativas consideradas

- **`requirements.txt`**: simples, mas não cobre metadados, extras, entry points
  e configuração de ferramentas. Rejeitado.
- **Poetry**: maduro e com lockfile, mas adiciona mais uma ferramenta e um
  formato próprio de configuração. Pode ser reconsiderado.
- **uv**: rápido, moderno e compatível com `pyproject.toml`; recomendado para o
  futuro, mas não adotado agora para manter a Fase 0 simples.
