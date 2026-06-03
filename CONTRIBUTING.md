# Contributing to CrisisLens

Thank you for your interest in contributing to CrisisLens! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/CrisisLens.git
cd CrisisLens
git remote add upstream https://github.com/Anandhu-p-tec/CrisisLens.git
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Write clean, well-documented code
- Add type hints to all functions
- Include docstrings (Google style)
- Add tests for new features

### 4. Commit
Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat(classification): Add support for new crisis type
docs(api): Update endpoint documentation
fix(geocoder): Handle timeout edge cases
refactor(core): Improve error handling
```

### 5. Push & Pull Request
```bash
git push origin feature/your-feature-name
```

Create PR with:
- Clear title and description
- Link to related issues
- Test results

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
```

## Code Style

- **Python**: PEP 8, enforced by Black
- **Type Hints**: Required for all functions
- **Docstrings**: Google style, all public methods
- **Testing**: Pytest with >80% coverage

## Testing

```bash
# Run all tests
pytest tests/ -v --cov=app

# Run specific module
pytest tests/test_classifier.py -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html
```

## Documentation

- Update README.md if adding features
- Add docstrings to all functions
- Update API docs for endpoint changes
- Include examples in code comments

## Pull Request Process

1. Ensure all tests pass: `pytest tests/ -v`
2. Format code: `black app/ tests/`
3. Run linter: `flake8 app/ tests/`
4. Update documentation
5. Request review from maintainers
6. Respond to feedback promptly

## Issues

- Check existing issues before creating new ones
- Use issue templates
- Provide reproducible examples
- Include system info (OS, Python version, etc.)

## Questions?

Open a discussion or ask in our community channels.

Happy contributing! 🎉
