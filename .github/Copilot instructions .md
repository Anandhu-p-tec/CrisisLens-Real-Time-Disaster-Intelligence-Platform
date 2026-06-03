# GitHub Copilot Instructions — CrisisLens

These instructions are authoritative. Copilot must follow them for every generation in this repository.

---

## Output Discipline — What You Must Never Generate

- Do not create README files, CHANGELOG files, or any `.md` documentation unless explicitly instructed by the developer in that exact prompt.
- Do not add inline comments that explain what a block of code does unless the code is genuinely non-obvious (e.g. a bitwise trick, a regex, a FAISS index parameter). Never write comments like `# initialize the model` or `# loop through tweets`.
- Do not generate example scripts, demo files, placeholder files, or `__init__.py` stubs beyond what is strictly needed for the module to be importable.
- Do not create `test_*.py` files unless the prompt explicitly says "write tests for X".
- Do not generate `.env.example`, `Makefile`, or `setup.py` unless asked.
- Do not add `if __name__ == "__main__"` blocks to module files. Only add them to files whose sole purpose is to be run as a script.
- Do not produce multiple alternative implementations. Generate one correct implementation.
- Do not explain what you just generated in a comment block at the top of the file.

---

## Naming Conventions — Absolute Rules

- No phase numbers, iteration numbers, or version suffixes in any filename or identifier. (`phase1_classifier.py` → wrong. `classifier.py` → correct.)
- No `_v2`, `_new`, `_final`, `_test`, `_temp` suffixes anywhere.
- No `utils.py` catch-all files. Name utility modules by their actual domain: `geocoding.py`, `text_preprocessing.py`, `severity_scoring.py`.
- Python files: `snake_case.py`
- Python classes: `PascalCase`
- Python functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- FastAPI routers: named after the resource they serve (`events.py`, `stream.py`, `health.py`)
- Pydantic models: suffix `Schema` or `Model` never both (`CrisisEventSchema`, not `CrisisEventModel`)

---

## File Generation Rules

Only generate a file when the prompt asks for it. Do not generate sibling files speculatively.

| Prompt asks for | Generate |
|---|---|
| A classifier | `classifier.py` only |
| A FastAPI router | The router file only |
| A Pydantic schema | The schema file only |
| A pipeline | The pipeline file only — not a runner, not a test |

---

## Architecture Constraints

- All configuration is loaded from environment variables via `pydantic-settings`. No hardcoded strings for API keys, model paths, or database URIs anywhere.
- All database access goes through the repository layer (`repository/`). No raw SQL in routers or service files.
- All LLM calls go through `services/llm_service.py`. No direct API client instantiation in classifiers, routers, or pipelines.
- Logging uses the standard `logging` module configured in `core/logging.py`. No `print()` statements in any non-script file.
- All inter-service data passed as typed Pydantic models. No raw dicts crossing module boundaries.
- Imports within the project are always absolute from the package root (`from app.services.classifier import CrisisClassifier`), never relative (`from ..services import ...`).

---

## Python Style

- Python 3.11+. Use `match` statements where appropriate. Use `TypeAlias` for complex types.
- Type-annotate every function signature — parameters and return type. No bare `Any` unless interfacing with an untyped third-party library, in which case add `# type: ignore` with a comment explaining why.
- Use `dataclasses.dataclass` for simple data containers, Pydantic `BaseModel` for anything that crosses an API or service boundary.
- Do not use mutable default arguments. Do not use `global`.
- Max line length: 100 characters.
- Prefer `pathlib.Path` over `os.path` for all filesystem operations.

---

## Dependency Rules

- Do not introduce a new dependency without it being in `pyproject.toml` or `requirements.txt` first.
- Do not use LangChain unless explicitly instructed. Use direct API clients (Anthropic SDK, Google Generative AI SDK) instead.
- Do not use `requests` — use `httpx` for all HTTP calls (async-compatible).
- Do not use `pickle` for model serialization. Use `safetensors` or the HuggingFace `save_pretrained` pattern.

---

## What Good Output Looks Like

A good Copilot generation in this repo:
- Is a single file with a clear, focused responsibility
- Has no markdown, no explanation comments, no placeholder TODOs (unless the prompt asked for a skeleton)
- Follows the directory structure in `ARCHITECTURE.md` exactly
- Is immediately runnable or importable without modification
- Contains no dead code, no commented-out blocks, no `pass` stubs unless the file is intentionally a skeleton