lint:
	uv run toml-sort pyproject.toml
	uv run ruff check --fix
	uv run ruff format
	uv run pydocstyle classification_automl/
	uv run bandit . -r -q -c pyproject.toml
	# uv run pylint classification_automl/
	# uv run mypy classification_automl/
