FROM python:3.11

RUN apt-get update \
    && apt-get -y install \
    python3-dev \
    libffi-dev \
    libnacl-dev \
    curl \
    ffmpeg

WORKDIR /usr/local/src/simple-discord-tts

COPY . /usr/local/src/simple-discord-tts

RUN pip install .

EXPOSE 8000

CMD ["python3", "-m", "simple-discord-tts.main"]
