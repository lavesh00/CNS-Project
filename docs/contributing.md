# Contributing to Agent Lucky

Thank you for your interest in contributing to Agent Lucky! 🍀

## How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in [Issues](https://github.com/lavesh00/agent-lucky/issues)
2. If not, create a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - System info (OS, Python version, model used)
   - Error logs

### Suggesting Features

1. Check [Discussions](https://github.com/lavesh00/agent-lucky/discussions)
2. Create a feature request issue with:
   - Clear use case
   - Expected behavior
   - Why it's useful

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests
5. Update documentation
6. Commit with clear messages (`git commit -m 'Add amazing feature'`)
7. Push to your fork
8. Create a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/agent-lucky.git
cd agent-lucky

# Install backend dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Run tests
pytest

# Run backend
python main.py --dev
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Run `black` for formatting
- Run `ruff` for linting

```bash
black backend/
ruff check backend/
```

### JavaScript
- Use ES6+ features
- Add JSDoc comments
- Follow Airbnb style guide

## Testing

- Write tests for new features
- Maintain test coverage above 80%
- Test with multiple models

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_planner.py

# With coverage
pytest --cov=backend --cov-report=html
```

## Documentation

- Update docs for new features
- Add examples
- Keep README up-to-date

## Commit Messages

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `chore:` Maintenance

Example: `feat: add support for Llama 3.1 models`

## Areas for Contribution

### High Priority
- VS Code UI panels implementation
- Additional project templates
- Model optimizations
- Better error handling

### Medium Priority
- Additional MCP servers
- More test coverage
- Performance improvements
- Documentation improvements

### Good First Issues
Look for issues labeled `good-first-issue`

## Questions?

- Discord: [Join our community](https://discord.gg/agentlucky)
- Discussions: [GitHub Discussions](https://github.com/lavesh00/agent-lucky/discussions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

