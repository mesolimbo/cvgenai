FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIPENV_VENV_IN_PROJECT=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libpango-1.0-0 \
      libpangoft2-1.0-0 \
 && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv

WORKDIR /app
COPY . .

# `sync` installs exactly what Pipfile.lock pins, with hash verification,
# and runs no dependency resolver — so the lockfile is the single source of truth.
RUN pipenv sync --dev

ENV PYTHONPATH=/app/src

CMD ["pipenv", "run", "pytest", "--cov=cvgenai", "--cov-report=term"]
