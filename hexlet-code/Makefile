install:
	uv sync

lint:
	uv run ruff check

build:
    ./build.sh

render-start:
    gunicorn task_manager.wsgi