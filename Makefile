build:
	poetry export --format requirements.txt --output requirements.txt \
	&& docker compose build
