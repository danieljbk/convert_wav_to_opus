# Contributing

📦 **Set up the project**

- Install Python 3.9 or newer.
- Create a virtual environment and activate it.
- Install the project in editable mode with development tools:

```bash
python -m pip install --upgrade pip
python -m pip install ".[dev]"
```

🧪 **Run quality checks before opening a pull request**

- `ruff check .` to lint the code.
- `mypy src` to ensure type safety.
- `pytest` to execute the test suite.

📝 **Making changes**

- Keep functions small and well tested.
- Update or add tests for any new behaviour.
- When updating the CLI, consider backwards compatibility for existing scripts.
- Document user-facing changes in `README.md`.

🙌 **Need help?**

Open a draft pull request early or file an issue describing the challenge. We're happy to collaborate.
