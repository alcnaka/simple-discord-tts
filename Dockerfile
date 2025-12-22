FROM ghcr.io/astral-sh/uv:python3.14-trixie

ENV UV_NO_DEV=1


RUN apt-get update \
    && apt-get -y install \
    python3-dev \
    libffi-dev \
    libnacl-dev \
    curl \
    ffmpeg

WORKDIR /usr/local/src/simple-discord-tts

COPY . /usr/local/src/simple-discord-tts

RUN uv sync --locked

EXPOSE 8000

CMD ["uv", "run", "python", "-m", "simple_discord_tts.main"]
