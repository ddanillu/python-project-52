install:
	uv sync

collectstatic:
	uv run manage.py collectstatic

migrate:
	uv run manage.py migrate

lint:
	uv run ruff check

build:
	./build.sh

render-start:
	gunicorn task_manager.wsgi

test:
	uv run manage.py test

test-users:
	uv run manage.py test task_manager.test_users -v2

test-statuses:
	uv run manage.py test task_manager.test_status -v2

test-tasks:
	uv run manage.py test task_manager.test_tasks -v2

test-labels:
	uv run manage.py test task_manager.test_labels -v2

test-filter:
	uv run manage.py test task_manager.test_filter -v2

test-coverage:
	uv run coverage run manage.py test task_manager && \
	uv run coverage xml

extract:
	uv run django-admin makemessages -l en

compile:
	uv run django-admin compilemessages