# Fase 0 — Fundação do Projeto

## 1. Objetivo

A Fase 0 não implementa áudio, interface gráfica nem inteligência artificial.
Ela prepara o repositório para que as fases seguintes comecem com uma base
organizada, reproduzível e documentada.

Ao final desta fase, o projeto deve ser capaz de:

- ser instalado em modo editável com `pip install -e ".[dev]"`;
- ser importado como `harmoniac`;
- executar um CLI mínimo (`harmoniac`) que imprime a versão;
- rodar testes, lint e verificação de tipos;
- evoluir com Git Flow e commits convencionais.

## 2. Escopo

### Dentro do escopo

- Empacotamento com `pyproject.toml` (PEP 621) e build backend `hatchling`.
- Layout `src/harmoniac/` com os subpacotes `core`, `dsp`, `audio` e `ui`.
- Ferramentas de qualidade: pytest, pytest-cov, ruff e mypy.
- Ambiente virtual com `venv` + `pip`.
- Estrutura inicial de documentação.
- Branches `develop` e `feature/fase-0-fundacao`.
- Testes de fumaça do pacote e do CLI.

### Fora do escopo

- Reprodução de áudio, mixer, time-stretch e metrônomo.
- Interface PyQt6.
- Demucs, Whisper e APIs de letras.
- Modelagem completa do JSON mestre.
- Push para o GitHub.

## 3. Decisões

### 3.1. `pyproject.toml` em vez de `requirements.txt`

O `pyproject.toml` concentra metadados, dependências, extras opcionais, entry
points e configuração de ferramentas. O `requirements.txt` não descreve o
pacote nem permite separar dependências pesadas de IA. A decisão completa está
em `docs/decisoes/0001-gerenciamento-de-dependencias.md`.

### 3.2. Layout `src/harmoniac`

O documento de arquitetura original mostrava `src/core`, `src/dsp`, `src/audio`
e `src/ui`. Adotamos `src/harmoniac/` porque:

- é o layout `src` recomendado para pacotes Python;
- evita que o diretório `src` seja confundido com um pacote;
- permite instalar o projeto com `pip install -e .`;
- deixa claro que `core`, `dsp`, `audio` e `ui` são submódulos de `harmoniac`.

### 3.3. Ambiente com `venv` + `pip`

O `uv` não está instalado no ambiente atual. Para manter a Fase 0 simples,
usamos o fluxo padrão:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

O `pyproject.toml` continua sendo a fonte única de verdade. Não há
`requirements.txt`.

### 3.4. `uv` e `uv.lock` (opcional)

- **`uv`** é um gerenciador moderno de ambientes e dependências Python. Ele lê o
  `pyproject.toml`, cria o ambiente, resolve e instala dependências e pode
  fixar a versão do Python.
- **`uv.lock`** é o arquivo de lock gerado pelo `uv`. Ele registra as versões
  exatas de todas as dependências (diretas e transitivas), com hashes, para
  tornar a instalação reproduzível. É o equivalente ao `package-lock.json` do
  npm ou ao `poetry.lock`.

Se o `uv` for adotado no futuro, o `uv.lock` deve ser versionado. A migração não
exige reescrever o `pyproject.toml`.

### 3.5. Licença

Adotamos **GPL-3.0-or-later** porque o PyQt6 é distribuído sob GPLv3 ou licença
comercial. Se o projeto optar por uma licença permissiva (MIT/Apache), será
necessário trocar o PyQt6 por PySide6 (LGPL) antes da implementação da UI.

### 3.6. Convenções

- Identificadores de código em inglês (padrão da indústria).
- Docstrings, comentários e documentação em português.
- Chaves do JSON mestre em português, conforme a especificação.
- Funções pequenas, puras quando possível, com type hints.
- Testes no padrão AAA (Arrange, Act, Assert).

## 4. Estrutura criada

```text
harmoniac/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── harmoniac/
│       ├── __init__.py
│       ├── __main__.py
│       ├── core/__init__.py
│       ├── dsp/__init__.py
│       ├── audio/__init__.py
│       └── ui/__init__.py
├── tests/
│   └── unit/test_smoke.py
├── assets/.gitkeep
├── data/.gitkeep
└── docs/
    ├── engenharia/fase-0-fundacao.md
    ├── decisoes/0001-gerenciamento-de-dependencias.md
    └── teoria/00-mapa-teoria-codigo.md
```

## 5. Arquivos criados

### 5.1. `pyproject.toml`

Define:

- build backend `hatchling`;
- nome, versão, descrição, licença e classificação do pacote;
- dependências principais;
- extras `dev`, `ai` e `lyrics`;
- entry point `harmoniac`;
- configuração de ruff, pytest, cobertura e mypy.

O extra `dev` é o único instalado nesta fase. Os extras `ai` e `lyrics` ficam
para as fases correspondentes.

### 5.2. `src/harmoniac/__init__.py`

Expõe a versão do pacote em `__version__`. É o ponto de entrada para
importações como `from harmoniac import __version__`.

### 5.3. `src/harmoniac/__main__.py`

Implementa `main()`, que imprime a versão atual. Permite:

```bash
python -m harmoniac
harmoniac
```

### 5.4. Subpacotes

- `core/`: modelos de domínio, contratos e estruturas de dados.
- `dsp/`: análise e processamento digital de sinais.
- `audio/`: reprodução, mixagem e buffers.
- `ui/`: interface gráfica com PyQt6.

Nesta fase eles contêm apenas docstrings.

### 5.5. `tests/unit/test_smoke.py`

Verifica:

- se a versão do pacote é `0.1.0`;
- se o CLI imprime `Harmoniac 0.1.0`.

Esses testes garantem que o pacote foi instalado corretamente e que o entry
point funciona.

### 5.6. `.gitignore`

Ignora ambientes virtuais, caches, artefatos de build, cobertura e o workspace
local `data/`. O arquivo `data/.gitkeep` mantém a pasta no repositório.

### 5.7. `README.md`

Apresenta o projeto, o status da Fase 0, a stack, a estrutura, os comandos de
instalação e teste, o roadmap e a licença.

### 5.8. `LICENSE`

Texto completo da GNU General Public License v3.0.

## 6. Comandos executados

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"

pytest
ruff check .
ruff format --check .
mypy src
harmoniac
```

## 7. Validação

Execução em 2026-10-21, com Python 3.12.3:

- `pytest`: **2 testes passando**, cobertura de 100% (4 statements);
- `ruff check .`: **All checks passed!**;
- `ruff format --check .`: **17 files already formatted**;
- `mypy src`: **Success: no issues found in 6 source files**;
- `harmoniac`: **Harmoniac 0.1.0**.

### Versões principais instaladas

| Pacote | Versão |
|---|---|
| Python | 3.12.3 |
| numpy | 2.5.4 |
| scipy | 1.18.1 |
| librosa | 1.0.0 |
| sounddevice | 0.5.6 |
| PyQt6 | 6.11.0 |
| pytest | 9.1.1 |
| pytest-cov | 7.1.0 |
| ruff | 0.17.1 |
| mypy | 2.4.0 |

As versões exatas das dependências transitivas não estão fixadas em um lockfile
nesta fase. Se a reprodutibilidade se tornar necessária, adotaremos `uv` e
versionaremos o `uv.lock`.

## 8. Git Flow

- `main`: versões estáveis.
- `develop`: integração contínua das features.
- `feature/fase-0-fundacao`: branch de trabalho desta fase.

Commits seguem o padrão convencional (`feat:`, `fix:`, `docs:`, `test:`,
`build:`, `chore:`). Ao final da fase, a feature é integrada em `develop` com
`--no-ff`.

## 9. Próximos passos

1. Revisar a validação e a estrutura com o aluno.
2. Iniciar a Fase 1: reprodução de um array NumPy com `sounddevice`.
3. Criar as primeiras notas teóricas sobre buffers, sample rate e underruns.
